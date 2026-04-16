# ForgeOps — Diário de construção

Um registro curto e honesto das decisões que moldaram este repositório.
Escrito conforme a construção avançou, para que leitores posteriores
entendam o *porquê*, não só o *o quê*.

---

## 0. Moldura de escopo

O ForgeOps foi construído de ponta a ponta como uma única iniciativa: "um
auditor de repositórios com IA, planejador de refatoração, engine de
documentação e workspace de engenharia agentico". O briefing foi explícito
sobre a barra de qualidade (nível portfólio, digno de GitHub, zero UI
placeholder) e igualmente explícito sobre o que pular (chamadas reais a LLM,
auth de usuário, pull de repo remoto — para v1).

**Decisões-chave de escopo tomadas no início:**

* Entregar com um **repositório demo imperfeito embutido** para que avaliadores
  nunca precisem fornecer input.
* **Zero dependência externa** em runtime — sem chaves de API de LLM, sem
  telemetria, sem analytics de terceiros.
* **Scoring determinístico.** Rodar o mesmo repo duas vezes, obter números
  idênticos.
* **Duas trilhas, uma sessão:** backend (FastAPI) e frontend (Next.js)
  construídos em paralelo sob o mesmo monorepo `apps/`.

---

## 1. Backend: FastAPI + Pydantic

**Framework.** FastAPI pela combinação zero-ceremony de schemas + OpenAPI +
upload async de arquivo. Models Pydantic v2 servem como validação e como
contrato para `apps/web/lib/types.ts`.

**Formato do pipeline.** `ingerir → varrer → detectar stack → pontuar →
montar achados → gerar relatórios`. Cada estágio é função pura da entrada. Só
o primeiro (`ingest`) e o último (`storage`) tocam disco fora do repositório
varrido.

**Segurança do ZIP primeiro.** `analyzer/zip_safe.py` foi escrito antes das
rotas porque é o único módulo que aceita input adversarial. Caminhos
absolutos, traversal `..`, symlinks, membros oversize e blowups de contagem
de arquivos todos levantam `SafeExtractionError` antes que qualquer coisa
seja comitada. Testado em
`test_safe_extraction_rejects_absolute_and_traversal`.

**O scanner é o hub.** Todo módulo a jusante lê o mesmo `ScanResult`. Isso
mantém o custo de adicionar um novo sinal de scoring em "adicionar um
contador, consumir". A lista de diretórios ignorados (`node_modules`,
`.venv`, `.git`, `dist`, …) vive em um lugar só.

**Scoring — deliberadamente legível.** A tentação de construir um rule engine
estilo plugin foi resistida. Sete funções de dimensão, um gerador de
problemas. Cada nota é uma sequência curta de deltas aditivos com um
rationale em linguagem simples anexado. Quando alguém pergunta "por que a
nota de documentação é 32?", a resposta é uma lista curta de booleans, não
uma DSL.

**Storage.** SQLite via stdlib `sqlite3`. Uma linha por sessão, payload como
JSON. A tabela é indexada para o painel "análises recentes". Thread-safe via
lock no nível do módulo. Esta é a escolha certa até haver múltiplos usuários
ou escritas concorrentes em escala real.

---

## 2. Frontend: Next.js 14 App Router

**Framework.** Next.js 14.2 com App Router. Server components para rotas que
se beneficiam de HTML inicial amigável a SEO (`/`, `/analysis/[id]`), client
components onde a interatividade vive (uploader, abas do dashboard).

**Tailwind com paleta custom pequena.** Dark-first (`bg.base=#0a0a12`) com
acento violeta. Tudo reutilizável foi promovido para uma classe de componente
dentro de `@layer components` no `globals.css`. Isso manteve o JSX limpo
(`className="panel"` em vez de cinco utilitários Tailwind) sem introduzir uma
dependência CSS-in-JS.

**Recharts para visualização.** Só dois gráficos — uma pizza sobre
`language_breakdown` e uma barra horizontal sobre severidade de problemas.
Ambos consomem dados já formados pelo backend, sem agregação no cliente. Se o
tamanho de bundle importar algum dia, estes devem ser carregados via
`next/dynamic`.

**Renderer de Markdown próprio.** `lib/markdown.tsx` tem ~120 linhas e
suporta headings, parágrafos, listas, code fences, tabelas, blockquotes,
hr, e inline code/bold/italic/links. Suficiente para os quatro relatórios
gerados e evita puxar uma dependência pesada de Markdown. Se HTML inline virar
necessário, trocar para `react-markdown` + `remark-gfm`.

**Download de relatórios.** Via `Blob` + click em âncora. Nenhum endpoint
extra necessário; o frontend já tem o Markdown em mãos.

---

## 3. Decisões notáveis

### Por que nenhum LLM no caminho de análise

Dois motivos. Primeiro, **determinismo**: o produto só funciona se as notas
forem estáveis entre execuções, para que o dashboard seja significativamente
comparável. Segundo, **demo zero-setup**: avaliadores conseguem rodar a
experiência completa em menos de dois minutos sem chaves ou billing. Uma
passada de *enriquecimento* por LLM que reescreve campos narrativos
(headline do sumário, objetivos das fases) sem tocar nas notas é uma extensão
razoável no futuro.

### Por que um demo embutido

Reviews de portfólio costumam falhar em "me dá um input de exemplo". O demo
aciona todos os caminhos de scoring: `.env` commitado (crítico), `build/`
commitado (limpeza), seções de README faltando (documentação), sem testes
(testes), sem CI (entrega), util de auth ingênuo (cheiro real). Vive em
`samples/demo-repo/` e é embutido na imagem Docker da API.

### Por que a saída standalone do Next.js

A imagem Docker `web` é construída a partir de `.next/standalone`, que
produz um `server.js` self-contained + `node_modules` mínimo. A imagem de
runtime fica pequena e o cold-start é rápido. O trade-off é um Dockerfile
multi-estágio — ok, dado que só há um.

### Por que `NEXT_PUBLIC_API_BASE_URL` como build arg

O bundle frontend assado no container precisa saber a URL da API. Passar
como build arg no `docker-compose.yml` mantém a config compose como fonte
única de verdade. Um deploy em produção sobrescreveria no build time.

---

## 4. Coisas que deram errado e como foram corrigidas

**Deprecação de `datetime.utcnow()`.** Python 3.12 emite `DeprecationWarning`.
Substituído cada chamada por
`datetime.now(timezone.utc).replace(tzinfo=None)` (mantém a semântica naive
que o resto do código assumia).

**Contagem dupla de `.env`.** Tanto o tracking `env_files` quanto o regex
genérico `_is_suspicious()` estavam marcando `.env`, então a demo mostrava
`security.secret_like_files` além de `security.env_committed`. Removida a
ramificação de `.env` em `_is_suspicious()` e desacopladas as duas regras.
Demo foi de 14 → 13 problemas, geral 44 → 46.

**Tailwind `bg-violet-500/12` rejeitado.** A escala de opacidade do Tailwind
pula 10 → 15 → 20; `/12` não existe. Substituído por um
`background: rgba(138, 104, 255, 0.14)` inline na regra `.btn-tab.active`,
para sobreviver a updates futuros do Tailwind.

**Mismatch de contexto no Dockerfile.** O Dockerfile inicial da API tinha
`context: ./apps/api` mas tentava `COPY samples ./samples` (fora do contexto).
Troquei ambos os serviços para `context: .` e prefixei os `COPY` com
`apps/api/…`.

**Pasta `public/` do Next.js ausente.** O builder standalone tolera `public/`
ausente, mas o `COPY --from=builder /app/public ./public` do Dockerfile web
não tolera. Adicionado `.gitkeep` para que a pasta sempre exista.

---

## 5. O que está totalmente funcionando

* Landing renderiza com hero + grid de features + pipeline "como funciona" +
  uploader drag-and-drop + lista de análises recentes.
* `POST /api/analyze/demo` → `200 OK`, `AnalysisSession` completo com 13
  problemas, 26 recomendações, 5 fases, 4 documentos gerados.
* `POST /api/analyze/upload` aceita ZIP multipart, faz streaming para disco,
  impõe limites de tamanho, roda o mesmo pipeline.
* `/analysis/[id]` renderiza o dashboard: hero do sumário, 10 chips de
  métricas rápidas, abas visão geral / notas / problemas / plano /
  relatórios / metodologia.
* Cada um dos quatro Markdowns gerados baixa como `.md` standalone.
* 6/6 testes pytest passam.
* `next build` sobe com sucesso; home ~3.95 kB, rota de análise ~111 kB.
* `docker compose up --build` sobe ambos os serviços saudáveis com volume
  SQLite.

---

## 6. O que está deliberadamente adiado

* **Ingestão por URL do GitHub.** A UX existe só para ZIP; ingestão de URL de
  repo público precisaria de clone com rate-limit + auth.
* **Auth de usuário & storage multi-tenant.** SQLite está ok para demos
  single-user.
* **Diff de screenshots / visão histórica de tendência.** A camada de storage
  já captura o suficiente para plotar nota-no-tempo, mas a UI para isso é
  trabalho futuro.
* **Export PDF.** Relatórios são exportados apenas em Markdown.
* **Passada de enriquecimento por LLM.** Os ganchos são óbvios (campos
  narrativos em `AnalysisSession`) mas fora do escopo para v1.

---

## 7. Checks de qualidade executados

* `cd apps/api && pytest` → 6 passaram
* `cd apps/web && npm run build` → sucesso, sem erros TypeScript
* Smoke: backend em :8765, frontend em :3789, `POST /api/analyze/demo`
  retornou sessão completa; `/analysis/{id}` retornou 200 com HTML completo.

O app foi feito para ser *revisado*, não só lido. Se você clonou o repo,
`docker compose up --build` é o caminho mais rápido para a experiência
completa.
