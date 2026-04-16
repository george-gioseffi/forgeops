<div align="center">

# ForgeOps

**Auditor de repositórios, planejador de refatoração e engine de documentação — com DNA de agente de IA.**

Envie um ZIP de qualquer repositório (ou clique em _Analisar repositório demo_) e receba uma
auditoria pronta para apresentação: nota de saúde em sete dimensões de engenharia,
backlog de problemas explicados, plano de execução em cinco fases e quatro relatórios
em Markdown prontos para exportar.

[Começo rápido](#-setup-local) · [Docker](#-setup-com-docker) · [Como a nota é calculada](docs/SCORING.md) · [Arquitetura](docs/ARCHITECTURE.md)

</div>

---

## Capturas de tela

> As capturas ficam em `assets/screenshots/`. Rode o app localmente para gerar as suas;
> o dashboard ao vivo é o melhor ângulo do que o ForgeOps entrega.

| Landing | Dashboard de análise |
|:---:|:---:|
| `assets/screenshots/landing.png` | `assets/screenshots/analysis.png` |

---

## Por que o ForgeOps

Auditoria de repositório normalmente chega como um checklist num e-mail. O ForgeOps
tenta um caminho diferente: trata o repositório como um produto sob revisão e
devolve um dossiê pronto para mostrar — nota, evidência e plano — em uma só
execução.

* **Baseado em fatos, não em achismos.** Toda nota, problema e recomendação remete
  a um arquivo ou manifesto que o scanner realmente viu. As heurísticas estão
  documentadas em [docs/SCORING.md](docs/SCORING.md), não escondidas num prompt.
* **Determinístico e offline.** Sem chamadas a LLM, sem chaves de API, sem
  telemetria. O mesmo repositório sempre produz o mesmo relatório — ideal para
  demos, CI e comparações reprodutíveis ao longo do tempo.
* **Um clique para "ver num repo real".** Um projeto de demonstração deliberadamente
  imperfeito — README fraco, `.env` commitado, sem testes, com `build/` versionado —
  exercita todos os caminhos do produto sem exigir que o avaliador traga seu
  próprio ZIP.

---

## Recursos

| | |
|---|---|
| **Nota de saúde em 7 dimensões** | Arquitetura, Manutenibilidade, Documentação, Testes, Entrega, Segurança, Limpeza — ponderadas em uma nota geral A–F |
| **Painel de problemas com evidência** | Cerca de 25 regras embutidas geram achados crítico / alto / médio / baixo com o arquivo que disparou a regra |
| **Plano de execução em 5 fases** | Estabilizar → Portões de qualidade → Arquitetura → Documentação → Pronto para release, cada fase com escopo de risco / esforço / impacto |
| **Quatro relatórios gerados** | Visão geral do repositório, revisão de arquitetura, relatório de dívida técnica e plano de ação — todos baixáveis em Markdown |
| **Detecção de stack** | Faz parse de `package.json`, `requirements.txt`, `pyproject.toml`, `Dockerfile`, `.github/workflows/` e outros para inferir frontend / backend / testes / banco / CI |
| **Quebra por linguagem e gráficos** | Gráficos de pizza e barras (Recharts) sobre a contagem real de extensões |
| **Demo embutido determinístico** | Projeto sintético que aciona todos os caminhos de scoring |
| **Ingestão segura de ZIP** | Proteção contra zip-slip, limites por arquivo / total de bytes, rejeição de caminhos suspeitos |
| **Sessões persistidas em SQLite** | Cada análise ganha um id estável; o painel "análises recentes" reabre execuções anteriores |
| **UI escura, acento violeta** | Componentes Tailwind desenhados à mão — paineis, chips, progresso, cartões de nota expansíveis |

---

## Percurso

1. **Abra a home.** Hero, estatísticas rápidas, grid de recursos, pipeline
   "como funciona" e uma área de drag-and-drop.
2. **Escolha a entrada.** Solte um ZIP ou clique em "Analisar repositório demo"
   para rodar contra o `samples/demo-repo` embutido.
3. **Acompanhe as fases.** O uploader mostra _enviando → analisando → pronto_ e
   então direciona para `/analysis/{id}`.
4. **Leia o dashboard.** Hero com nota + pontos fortes / frágeis, chips de
   métricas rápidas e seis abas:
   * **Visão geral** — pizza de linguagens, distribuição de problemas, painel de stack, cartões de nota
   * **Notas** — cartões expansíveis por dimensão com rationale / positivos / preocupações / recomendações + tabela de metodologia
   * **Problemas** — lista filtrável com evidência e correção sugerida
   * **Plano** — cinco fases com chips de risco / esforço / impacto e itens por fase
   * **Relatórios** — preview em abas dos quatro documentos em Markdown + download
   * **Metodologia** — pesos e rationale de cada dimensão
5. **Exporte.** Cada relatório baixa como um `.md` independente.

---

## Arquitetura em uma imagem

```
┌────────────────┐         ZIP multipart          ┌──────────────────┐
│  Next.js 14    │ ────────────────────────────►  │  FastAPI         │
│  App Router    │ ◄──────────  JSON  ──────────  │  (Python 3.12)   │
│  Tailwind + RC │                                 │                  │
└────────────────┘                                 │  ┌────────────┐  │
                                                   │  │ zip-safe   │  │
                                                   │  │ scanner    │  │
                                                   │  │ frameworks │  │
                                                   │  │ scoring    │  │
                                                   │  │ generators │  │
                                                   │  └─────┬──────┘  │
                                                   │        ▼         │
                                                   │    SQLite        │
                                                   │  (forgeops.db)   │
                                                   └──────────────────┘
```

Mapa completo em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Mecânica da análise

O pipeline do backend é uma função em seis estágios. Cada estágio é puro sobre
sua entrada e pode ser testado isoladamente (veja `apps/api/tests/test_analyzer.py`).

1. **Ingestão** — `POST /api/analyze/upload` faz streaming do upload multipart
   para disco (limitado por `FORGEOPS_MAX_UPLOAD_BYTES`).
   `zip_safe.extract_zip_safely` rejeita caminhos absolutos, travessia (`..`),
   symlinks e membros acima do limite.
2. **Varredura** — `scanner.scan_repository` percorre a árvore uma vez, poda
   diretórios ruidosos (`node_modules`, `.git`, `dist`, `.venv`, …), classifica
   cada arquivo pela extensão e monta contadores para código / testes / configs
   / docs / binários / caminhos suspeitos / arquivos grandes.
3. **Detecção de stack** — `frameworks.detect_stack` faz parse dos manifestos
   (`package.json`, `requirements.txt`, `pyproject.toml`) e de marcadores de
   diretório (`.github/workflows/`, `Dockerfile`, `docker-compose.yml`) para
   preencher frontend / backend / testes / banco / CI / container e inferir o
   tipo de projeto.
4. **Scoring** — sete funções em `scoring/dimensions.py` retornam cada qual um
   `DimensionResult` com score, rationale, positivos, preocupações e
   recomendações. Os pesos são fixos e estão publicados em
   [docs/SCORING.md](docs/SCORING.md).
5. **Montagem dos achados** — `scoring/issues.py` emite cerca de 25 regras
   determinísticas. `scoring/recommendations.py` transforma problemas + dimensões
   fracas num backlog priorizado (fazer agora / em seguida / depois).
   `scoring/plan.py` distribui a remediação em cinco fases.
6. **Geração dos relatórios** — `generators/markdown.py` renderiza quatro
   documentos em Markdown (visão geral, revisão de arquitetura, dívida técnica,
   plano de ação) costurados a partir dos fatos acima — sem template vazio, sem LLM.

Tudo é persistido como um único JSON em `analyses.payload`, indexado pelo id
de sessão que o frontend usa na rota.

---

## Metodologia de scoring

A nota geral é a soma ponderada de sete dimensões:

| Dimensão               | Peso | Sinais                                                                         |
|------------------------|:----:|--------------------------------------------------------------------------------|
| Documentação           | 0.18 | Profundidade do README, `docs/`, CHANGELOG, CONTRIBUTING, LICENSE, `.env.example` |
| Testes                 | 0.18 | Arquivos de teste, proporção teste/código, runner detectado, presença de e2e   |
| Arquitetura            | 0.15 | Separação frontend/backend, formato monorepo, profundidade, coerência de framework |
| Entrega & DevEx        | 0.15 | Config de CI, containerização, config de lint + formatter                      |
| Manutenibilidade       | 0.14 | Mix código/assets, peso de binários, arquivos grandes, lockfile, poluição no topo |
| Higiene de Segurança   | 0.10 | `.env` commitado, `.gitignore` presente, nomes de arquivo suspeitos            |
| Limpeza do Repositório | 0.10 | Lixo de SO, `build/`/`dist/` commitados, `node_modules` na raiz                |

`geral = round(Σ score_i · peso_i)`. Notas: **A** ≥ 90, **B** ≥ 80, **C** ≥ 70,
**D** ≥ 60, **F** caso contrário. Lista completa das regras em
[docs/SCORING.md](docs/SCORING.md).

---

## Relatórios gerados

Cada análise produz quatro documentos em Markdown que aparecem na aba **Relatórios**:

| Slug | Conteúdo |
|---|---|
| `repository-overview` | Sumário executivo de uma página: nota, formato, stack, métricas de destaque |
| `architecture-review` | Estrutura, layout de topo, frameworks detectados, observações arquiteturais |
| `technical-debt-report` | Inventário de problemas agrupado por severidade com evidência |
| `action-plan` | O plano de cinco fases renderizado como checklists |

Os quatro são exportados como `.md` com um único clique.

---

## Stack

**Frontend** — Next.js 14 (App Router), React 18, TypeScript 5, Tailwind 3,
Recharts, lucide-react, tailwind-merge + clsx.

**Backend** — FastAPI 0.115, Pydantic 2, uvicorn, `python-multipart`, `sqlite3`
da stdlib.

**Ferramental** — pytest, Docker + docker-compose, saída `standalone` do Next.js.

Nenhum LLM / chave de API / serviço de analytics externo é usado em qualquer
parte da stack.

---

## Setup local

Requisitos: **Python 3.11+** e **Node 20+**.

```bash
# 1. Backend
cd apps/api
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn forgeops.main:app --reload --port 8000

# 2. Frontend (em outro terminal)
cd apps/web
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Depois abra <http://localhost:3000>. Clique em **Analisar repositório demo**
para rodar contra o sample embutido — sem upload necessário.

### Variáveis de ambiente

Copie `.env.example` → `.env` na raiz (ou exporte as variáveis no shell). Todas
as variáveis são opcionais; há defaults sensatos embutidos.

### Testes

```bash
cd apps/api
pytest
```

Seis testes cobrem o extrator zip-safe, o scanner, a detecção de stack, o
scoring, a geração de problemas e a geração de documentos.

---

## Setup com Docker

```bash
docker compose up --build
```

* API: <http://localhost:8000>
* Web: <http://localhost:3000>

A imagem web é construída a partir da saída `standalone` do Next.js (runtime
mínimo). A imagem da API embute `samples/demo-repo`, então o fluxo "Analisar
demo" funciona dentro do container sem mount adicional. O SQLite persiste em
um volume nomeado (`forgeops-data`).

---

## Fluxo do demo

O demo em `samples/demo-repo/` é intencionalmente imperfeito para que todos os
caminhos de scoring sejam exercitados na primeira execução. Ele tem:

* Um README curto, sem seção de setup
* Sem LICENSE, sem CHANGELOG, sem CONTRIBUTING
* Sem testes, sem CI, sem Dockerfile, sem config de linter/formatter
* Um `.env` commitado — aciona um problema crítico
* Um `build/bundle.js` commitado — aciona um problema de limpeza
* Apenas `node_modules/` no `.gitignore`
* Util de autenticação ingênuo (`server/utils/auth.js`) e Express + Mongoose escritos à mão

Headline esperada: **Geral 46, nota F, 13 problemas, 26 recomendações, 5 fases.**

---

## Estrutura do projeto

```
ops/
├─ apps/
│  ├─ api/                     # Backend FastAPI
│  │  ├─ forgeops/
│  │  │  ├─ analyzer/          # zip_safe, scanner, frameworks, languages
│  │  │  ├─ scoring/           # dimensions, issues, recommendations, plan
│  │  │  ├─ generators/        # escritor de relatório Markdown
│  │  │  ├─ storage/           # store SQLite
│  │  │  ├─ api/               # rotas FastAPI
│  │  │  ├─ models/            # schemas Pydantic
│  │  │  ├─ config.py          # dataclass de settings
│  │  │  └─ main.py            # fábrica do app
│  │  ├─ tests/                # suite pytest
│  │  ├─ Dockerfile
│  │  ├─ requirements.txt
│  │  └─ README.md
│  └─ web/                     # Frontend Next.js 14
│     ├─ app/                  # rotas App Router
│     ├─ components/
│     │  ├─ analysis/          # widgets do dashboard
│     │  ├─ landing/           # home
│     │  ├─ shared/            # Logo, Nav, Footer
│     │  └─ ui/                # primitivas base
│     ├─ lib/                  # client de API, tipos, utils, renderer Markdown
│     ├─ Dockerfile
│     └─ package.json
├─ samples/demo-repo/          # repositório imperfeito embutido
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ SCORING.md
│  └─ BUILD_LOG.md
├─ assets/screenshots/
├─ docker-compose.yml
├─ .env.example
├─ LICENSE
└─ README.md
```

---

## Roadmap

* Puxar repositórios direto de uma URL do GitHub (público + PAT)
* Deep links "abrir no VS Code" por problema
* Visão histórica: sobrepor duas análises do mesmo repo para mostrar o delta
* Exportar um dossiê PDF de uma página além dos quatro relatórios Markdown
* Perfis de scoring plugáveis (startup, enterprise, biblioteca, jogo)

---

## Melhorias futuras

* Trocar o renderer de Markdown manual por um mais robusto (remark-react) se
  suporte a HTML inline virar requisito.
* Substituir SQLite por Postgres quando cenários multi-usuário importarem; a
  camada de storage é pequena de propósito e isolada atrás de `AnalysisStore`.
* Embrulhar Recharts com `next/dynamic` para reduzir o bundle da rota de análise.
* Opcional: uma passada LLM que apenas *enriquece* os campos narrativos — sem
  interferir nas notas e problemas, que continuam determinísticos.

---

## Licença

[MIT](LICENSE) © 2026 ForgeOps.
