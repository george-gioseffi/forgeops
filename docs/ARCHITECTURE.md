# ForgeOps — Arquitetura

Este documento é o mapa que você lê *antes* do código. Cobre como o repositório
está organizado, como uma única análise flui de ponta a ponta e qual módulo é
dono de cada responsabilidade.

---

## 1. Layout do monorepo

```
ops/
├─ apps/
│  ├─ api/     # serviço FastAPI
│  └─ web/     # cliente Next.js 14 App Router
├─ samples/demo-repo/     # projeto imperfeito embutido usado pelo botão "Analisar demo"
├─ docs/                  # esta pasta
├─ assets/screenshots/
├─ docker-compose.yml
├─ .env.example
└─ LICENSE
```

Frontend e backend são desacoplados de propósito. O contrato entre eles é o
formato JSON de `AnalysisSession` (Pydantic no backend,
`apps/web/lib/types.ts` no frontend). Nenhum código é compartilhado
diretamente.

---

## 2. Backend (`apps/api`)

### Layout do pacote

```
forgeops/
├─ analyzer/
│  ├─ zip_safe.py       # primitiva de extração segura
│  ├─ scanner.py        # caminhada na árvore + classificação + contadores
│  ├─ frameworks.py     # detecção de stack a partir de manifestos
│  └─ languages.py      # extensão → (linguagem, é_código)
├─ scoring/
│  ├─ dimensions.py     # 7 funções de scoring
│  ├─ issues.py         # ~25 regras determinísticas
│  ├─ recommendations.py# backlog agora / em seguida / depois
│  └─ plan.py           # plano de execução em 5 fases
├─ generators/
│  └─ markdown.py       # 4 escritores de relatório Markdown
├─ storage/
│  └─ sqlite_store.py   # AnalysisStore (save / get / list_recent)
├─ api/
│  └─ routes.py         # router FastAPI
├─ models/
│  └─ schemas.py        # models Pydantic v2 de request/response
├─ config.py            # dataclass Settings + singleton SETTINGS
└─ main.py              # create_app() e app de nível de módulo
```

### Pipeline de request

```
Upload HTTP
    │
    ▼
routes.py  ─► streaming para disco, limite de bytes
    │
    ▼
analyzer/zip_safe.py  ─► rejeita traversal / absoluto / symlink / oversize
    │
    ▼
analyzer/scanner.py  ─► ScanResult (contadores, listas categorizadas)
    │
    ▼
analyzer/frameworks.py  ─► StackDetection (frameworks, runners, CI, bancos)
    │
    ▼
scoring/dimensions.py  ─► 7 × DimensionResult
scoring/issues.py      ─► list[Issue]
scoring/recommendations.py ─► list[Recommendation]
scoring/plan.py        ─► list[Phase]
    │
    ▼
generators/markdown.py  ─► 4 × GeneratedDocument
    │
    ▼
storage/sqlite_store.py  ─► AnalysisStore.save(session)
    │
    ▼
Resposta JSON (AnalysisSession)
```

Cada estágio é puro sobre sua entrada. As únicas fronteiras de I/O são:

* Leituras de disco dentro de `analyzer/scanner.py` (árvore de arquivos +
  manifestos)
* Escritas no SQLite no fim (`storage/sqlite_store.py`)

É isso que mantém os testes rápidos e permite exercitar o engine de scoring
contra fixtures montadas na memória, sem extração real.

### Decisões de projeto

**Scoring determinístico e heurístico.** Sem LLM; sem aleatoriedade. Cada
dimensão é uma função pequena com aritmética simples e rationale explícito.
Quando um avaliador pergunta "por que a nota de documentação é 32?", a resposta
é uma lista curta de booleans: existe README, passa de 200 chars, tem seção
"usage" etc. Veja
[`scoring/dimensions.py`](../apps/api/forgeops/scoring/dimensions.py) e
[docs/SCORING.md](SCORING.md).

**Uma varredura, muitos leitores.** `scan_repository` percorre a árvore
exatamente uma vez e produz um `ScanResult` rico. Todo módulo a jusante
(detecção de stack, scoring, problemas, plano) lê desse resultado. O custo de
adicionar uma regra nova é ínfimo — sem I/O extra.

**Extração segura por construção.** `zip_safe.extract_zip_safely` impõe:

* sem caminhos absolutos
* sem traversal `..`
* sem caminhos que escapam de `dest_dir` depois do `realpath`
* sem symlinks
* limites de bytes totais + bytes por arquivo + quantidade de arquivos
* detecção de single-top-level-folder (desembrulha ZIPs estilo GitHub)

Qualquer coisa que falhe levanta `SafeExtractionError` antes de um único byte
ser gravado no destino.

**SQLite como store fino.** A sessão é serializada como um blob JSON único
(coluna `payload`). Lookup é por id; um índice pequeno
`id, repo_name, created_at, status, overall, grade` é mantido para o painel
"análises recentes". Thread-safe via lock no nível do módulo; uma conexão por
`AnalysisStore`.

### Modelo de dados

Definido em [`models/schemas.py`](../apps/api/forgeops/models/schemas.py).
Formato do topo (abreviado):

```python
class AnalysisSession(BaseModel):
    id: str
    repo_name: str
    source_type: Literal["upload", "demo"]
    status: Literal["complete", "failed"]
    created_at: datetime

    summary: ExecutiveSummary | None          # headline, risk_level, destaques
    repository_stats: RepositoryStats | None  # totais, language_breakdown
    detected_stack: StackDetection | None     # frameworks, runners, CI, bancos

    scores: list[DimensionScore]              # 7 dimensões ponderadas
    issues: list[Issue]                       # severidade, categoria, evidência, recomendação
    recommendations: list[Recommendation]     # prioridade, rationale, ação
    phases: list[Phase]                       # nome, objetivo, risco, esforço, impacto, items[]
    generated_documents: list[GeneratedDocument]  # slug, título, markdown
```

### Superfície da API

| Método | Path                              | Função                                        |
|--------|-----------------------------------|-----------------------------------------------|
| GET    | `/health`                         | Liveness probe                                |
| GET    | `/api/config`                     | Expõe config runtime segura para o web        |
| GET    | `/api/analysis`                   | Análises recentes (id / nome / geral)         |
| GET    | `/api/analysis/{id}`              | Payload completo da sessão                    |
| GET    | `/api/analysis/{id}/documents`    | Os 4 documentos Markdown gerados              |
| POST   | `/api/analyze/demo`               | Roda o pipeline contra `samples/demo-repo`    |
| POST   | `/api/analyze/upload`             | Análise de ZIP multipart                      |

---

## 3. Frontend (`apps/web`)

### Layout de rotas

```
app/
├─ layout.tsx               # shell global, <Nav />, <Footer />
├─ page.tsx                 # landing (Hero, UploadDropzone, features, recent)
├─ globals.css              # layer Tailwind + utilitários próprios (.panel, .btn-*, .prose-mini)
└─ analysis/[id]/
   ├─ page.tsx              # server component, fetchAnalysis()
   ├─ loading.tsx           # grid de skeletons
   └─ not-found.tsx         # painel 404
```

### Layout de componentes

```
components/
├─ ui/           Card, Badge, Progress, Tabs, Skeleton      (primitivas base)
├─ shared/       Logo, Nav, Footer
├─ landing/      Hero, UploadDropzone, FeatureGrid,
│                HowItWorks, RecentAnalyses
└─ analysis/     AnalysisView (topo, 6 abas)
                 SummaryHero, QuickMetrics, ScoreCards,
                 LanguageChart, IssueSummary, StackPanel,
                 IssueList, PhasedPlan, RecommendationsPanel,
                 DocsPreview, MethodologyPanel
```

`AnalysisView` é dono do estado `tab` e delega a um widget dedicado por aba
(`overview`, `scores`, `issues`, `plan`, `docs`, `methodology`).

### Código de biblioteca

```
lib/
├─ api.ts       client fetch tipado (fetchAnalysis, fetchDocuments, analyzeUpload, analyzeDemo)
├─ types.ts     espelhos TS do schema Pydantic
├─ utils.ts     cn, formatBytes, formatRelativeTime, gradeColor, severityColor
└─ markdown.tsx renderer Markdown pequeno próprio (headings, listas, code fences,
                tabelas, blockquotes, links seguros)
```

O renderer de Markdown é próprio (~120 linhas). Suficiente para os quatro
relatórios gerados e evita carregar uma dependência pesada de Markdown. Se
suporte a HTML inline virar requisito, trocar por `react-markdown` +
`remark-gfm`.

### Estilo

Tailwind 3 com uma paleta custom pequena (`bg.base`, `bg.raised`, `bg.card`,
`bg.subtle`, `bg.border`, `accent`, tons extras de violeta). Tudo reutilizável é
promovido para uma classe de componente dentro de `@layer components` no
`app/globals.css`: `.panel`, `.panel-hoverable`, `.btn-primary`, `.btn-ghost`,
`.btn-tab`, `.chip`, `.chip-accent`, `.section-title`, `.stat-card` e um
conjunto `.prose-mini` para Markdown renderizado.

### Frontend → backend

Rota via `NEXT_PUBLIC_API_BASE_URL`. O client da API (`lib/api.ts`) mantém a
superfície pequena:

```ts
fetchAnalysis(id)            // GET  /api/analysis/{id}
fetchDocuments(id)           // GET  /api/analysis/{id}/documents
fetchRecentAnalyses(limit?)  // GET  /api/analysis
analyzeDemo()                // POST /api/analyze/demo
analyzeUpload(file)          // POST /api/analyze/upload  (FormData)
fetchHealth()                // GET  /health
```

Todas as respostas são tipadas contra `lib/types.ts`, que é mantido em sincronia
manualmente com `schemas.py`. É pequeno o bastante para que divergências
apareçam em code review.

### Estratégia de renderização

* `app/page.tsx` é server-rendered e busca análises recentes.
* `app/analysis/[id]/page.tsx` é `dynamic = "force-dynamic"` e busca a sessão
  no servidor, depois passa para o client component `AnalysisView`. Isso mantém
  o HTML inicial da rota significativo (bom para metadata) enquanto abas e
  filtros vivem no cliente.

---

## 4. Armazenamento

Um arquivo SQLite em `apps/api/data/forgeops.db` (o caminho é configurável via
`FORGEOPS_DATA_DIR`). Schema:

```sql
CREATE TABLE analyses (
  id          TEXT PRIMARY KEY,
  repo_name   TEXT NOT NULL,
  source_type TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  status      TEXT NOT NULL,
  overall     INTEGER,
  grade       TEXT,
  payload     TEXT NOT NULL     -- JSON completo de AnalysisSession
);
```

Razões:

* Mantém a superfície de query trivial (get por id, listar recentes).
* Todo novo campo em `AnalysisSession` é automaticamente persistido.
* Fácil de inspecionar com `sqlite3` em caso de necessidade.

---

## 5. Deploy

O `docker-compose.yml` constrói ambas as imagens a partir da raiz do repositório:

* `api` → `apps/api/Dockerfile` (python:3.12-slim, embute `samples/demo-repo`)
* `web` → `apps/web/Dockerfile` (node:20-alpine multi-stage, saída standalone)

A API expõe um healthcheck em `/health` que o compose consulta. A API grava
o SQLite no volume nomeado `forgeops-data`, então o estado sobrevive a restarts.

Em produção, `NEXT_PUBLIC_API_BASE_URL` é o botão principal: setar em build
time (docker-compose passa como `--build-arg`) para que o bundle do navegador
saiba como alcançar a API.

---

## 6. Testes

`apps/api/tests/test_analyzer.py` cobre os caminhos críticos:

1. A extração de ZIP rejeita traversal e caminhos absolutos.
2. O scanner categoriza uma fixture realista em código / testes / configs / docs.
3. A detecção de stack pega Python + CI.
4. Scoring de um repo "limpo" produz nota alta.
5. Scoring de um repo "fraco" dispara os problemas críticos (`.env` commitado,
   sem README, sem LICENSE, sem testes).
6. Os quatro documentos são gerados com corpo Markdown não-vazio.

```bash
cd apps/api
pytest -v
```

Fixtures são montadas em memória — os testes não precisam do demo embutido.

---

## 7. Trade-offs & não-objetivos

**O que o ForgeOps não é.** Não é um analisador estático, não é scanner de
segurança e não é linter. Não faz parse de código para control flow, AST ou
dataflow. Opera inteiramente no nível do *formato* do repositório — que é
exatamente a camada que a maioria das auditorias pula.

**Por que nenhum LLM.** Dois motivos. Primeiro, determinismo: as notas
precisam ser comparáveis entre execuções para o dashboard fazer sentido.
Segundo, zero-setup: a demo funciona sem chaves de API, então qualquer pessoa
avaliando o repo tem a experiência completa em menos de dois minutos. Uma
passada de *enriquecimento* por LLM para as seções narrativas é uma extensão
razoável no futuro — mas não deve mexer nas notas.

**Por que SQLite.** A superfície de storage é pequena e read-heavy. SQLite
mantém ops trivial e é trivialmente substituível porque toda persistência
passa por uma única classe `AnalysisStore`.
