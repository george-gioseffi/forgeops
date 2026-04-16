# ForgeOps — Metodologia de scoring

Este documento é a fonte de verdade para como um repositório chega à sua nota.
Todo número que a UI mostra remete a uma das heurísticas abaixo.

A implementação de referência vive em
[`apps/api/forgeops/scoring/`](../apps/api/forgeops/scoring/):

* `dimensions.py` — as sete funções de scoring
* `issues.py` — as ~25 regras determinísticas que emitem achados
* `recommendations.py` — transforma problemas + dimensões fracas em um backlog priorizado
* `plan.py` — distribui a remediação em cinco fases

Todo o scoring é determinístico. Sem LLM. Sem aleatoriedade. O mesmo
repositório sempre produz o mesmo relatório.

---

## 1. As sete dimensões

Cada dimensão é uma função da saída do scanner (`ScanResult`) e, quando
relevante, da detecção de stack (`StackDetection`). Cada uma retorna um
`DimensionResult` com:

* `score` — limitado a 0–100
* `weight` — fixo, listado abaixo
* `rationale` — explicação em uma linha
* `positives`, `concerns`, `recommendations` — trilha de auditoria mostrada na UI

### Pesos

| Chave           | Dimensão               | Peso |
|-----------------|------------------------|:----:|
| documentation   | Documentação           | 0.18 |
| testing         | Testes                 | 0.18 |
| architecture    | Arquitetura            | 0.15 |
| delivery        | Entrega & DevEx        | 0.15 |
| maintainability | Manutenibilidade       | 0.14 |
| security        | Higiene de Segurança   | 0.10 |
| cleanliness     | Limpeza do Repositório | 0.10 |

`geral = round(Σ score_i · peso_i)`. As notas seguem os cortes padrão
(ver §5).

### Documentação (0.18)

| Sinal | Pontos |
|---|:---:|
| README existe e tem > 200 chars | +6 |
| README tem seção setup / install / getting-started | +6 |
| README tem usage ou exemplos | +5 |
| README tem seção features ou architecture | +4 |
| README contém blocos de código | +3 |
| README > 1500 chars | +4 |
| README menciona licença | +2 |
| Pasta `docs/` com arquivos dedicados | +20 |
| CHANGELOG presente | +6 |
| CONTRIBUTING presente | +6 |
| CODEOWNERS presente | +6 |
| LICENSE presente | +12 |
| `.env.example` / sample env | +10 |
| Doc de arquitetura dentro de `docs/` | +5 |
| Doc de API dentro de `docs/` | +5 |

As pontuações são limitadas a 100. Só o componente README fecha em 30.

### Testes (0.18)

A base é função da razão arquivos de teste / arquivos de código:

| Condição                               | Base |
|----------------------------------------|:----:|
| Zero arquivos de teste                 | 5    |
| Razão ≥ 0.03 (muito rasa)              | 20   |
| Razão ≥ 0.10                           | 35   |
| Razão ≥ 0.10 (fina, mais do que smoke) | 55   |
| Razão ≥ 0.25 (saudável)                | 72   |

Bônus:

* Runner de teste detectado nos manifestos (pytest / Jest / Vitest / …) → +15
* Playwright ou Cypress detectado → +8

### Arquitetura (0.15)

| Sinal | Delta |
|---|:---:|
| Base                                                      | 55 |
| `frontend/` + `backend/` (ou `apps/` / `packages/`)       | +15 |
| Tipo de projeto inferido ≠ Desconhecido                   | +5 |
| Profundidade de diretórios > 12                           | -8 |
| Profundidade de diretórios 9–12                           | -4 |
| Muitas pastas pequenas (arquivos/dirs < 1.5 e > 30 arquivos) | -4 |
| Linguagem primária alinhada com o framework detectado     | +8 |
| CODEOWNERS presente                                       | +5 |

### Entrega & DevEx (0.15)

| Sinal | Delta |
|---|:---:|
| Base                                               | 30 |
| Workflow de CI detectado                           | +30 |
| Containerização (Dockerfile / compose)             | +20 |
| Config de lint (ESLint / Ruff / flake8 / …)        | +10 |
| Config de formatter (Prettier / Black / …)         | +10 |

### Manutenibilidade (0.14)

| Sinal | Delta |
|---|:---:|
| Base                                                         | 60 |
| Arquivos de código ≥ 40 % dos arquivos                       | +8  |
| Arquivos de código < 15 %                                    | -6  |
| Arquivos binários > 30 % dos arquivos                        | -10 |
| Mais de 3 arquivos > 1 MB                                    | -6  |
| 4+ arquivos de config                                        | +6  |
| Mais de 14 pastas no topo                                    | -4  |
| Lockfile de dependências commitado                           | +6  |

### Higiene de Segurança (0.10)

| Sinal | Delta |
|---|:---:|
| Base                                                       | 80 |
| Cada arquivo suspeito / que parece segredo                 | -15 (limitado a -55) |
| `.env` commitado sem exemplo sanitizado                    | -20 |
| `.env.example` presente sem `.env` cru                     | +8  |
| `.gitignore` presente                                      | +4  |
| Containerização presente                                   | +3  |

### Limpeza do Repositório (0.10)

| Sinal | Delta |
|---|:---:|
| Base                                                              | 85 |
| Lixo de SO (.DS_Store, Thumbs.db, …)                              | -5 cada, limite -20 |
| `dist/` / `build/` / `out/` commitados                            | -10 |
| `node_modules/` na raiz                                           | -25 |
| 5+ arquivos grandes                                               | -10 |
| Repositório vazio                                                 | → 0 |
| Repositório < 4 arquivos (placeholder)                            | -15 |
| README + LICENSE + manifesto todos presentes                      | +5  |

---

## 2. Regras de problemas

Cada regra é uma one-liner: dado um `ScanResult` e um `StackDetection`, emite
um `IssueItem` com severidade, evidência e uma correção recomendada. As
severidades mapeiam em cores da UI: **crítico** (vermelho), **alto** (laranja),
**médio** (violeta), **baixo** (cinza).

### Documentação & legal

| ID | Severidade | Dispara quando… |
|---|:---:|---|
| `docs.readme.missing`       | alto     | não há README.* na raiz |
| `docs.readme.thin`          | médio    | README < 400 chars |
| `docs.readme.no_setup`      | médio    | README sem seção setup/install |
| `docs.folder.missing`       | médio    | sem pasta `docs/` |
| `docs.contributing.missing` | baixo    | sem arquivo CONTRIBUTING |
| `docs.changelog.missing`    | baixo    | sem arquivo CHANGELOG |
| `legal.license.missing`     | alto     | sem arquivo LICENSE |

### Testes

| ID | Severidade | Dispara quando… |
|---|:---:|---|
| `testing.none`       | alto    | zero arquivos de teste |
| `testing.thin`       | médio   | razão < 0.10 |
| `testing.no_runner`  | médio   | nenhum runner de teste reconhecido nos manifestos |

### Entrega

| ID | Severidade | Dispara quando… |
|---|:---:|---|
| `ci.missing`            | alto   | nenhum workflow de CI detectado |
| `delivery.no_docker`    | médio  | sem Dockerfile / compose |
| `quality.no_lint`       | médio  | sem config de lint |
| `quality.no_formatter`  | baixo  | sem config de formatter |

### Segurança

| ID | Severidade | Dispara quando… |
|---|:---:|---|
| `security.env_committed`     | crítico | `.env` commitado sem `.env.example` |
| `config.no_env_example`      | médio   | sem `.env.example` |
| `security.secret_like_files` | alto    | nomes de arquivo suspeitos (keys, secrets, pems…) |

### Higiene

| ID | Severidade | Dispara quando… |
|---|:---:|---|
| `hygiene.no_gitignore`            | médio    | sem `.gitignore` |
| `hygiene.node_modules_committed`  | crítico  | `node_modules/` na raiz |
| `hygiene.build_artifacts`         | médio    | `build/` ou `dist/` na raiz |
| `hygiene.large_files`             | baixo    | 3+ arquivos > 1 MB |
| `architecture.deep_tree`          | médio    | profundidade de diretórios > 12 |

A evidência é preenchida a partir do `ScanResult` (ex.: nomes de arquivos,
contagens, tamanhos) para que cada achado renderize com uma lista "por que
isto foi apontado".

---

## 3. Backlog de recomendações

`scoring/recommendations.py` produz uma lista priorizada em dois passos:

1. **Mapa severidade → prioridade.** Cada problema vira uma recomendação
   (crítico/alto → `now`, médio → `next`, baixo → `later`).
2. **Recomendações por dimensão.** Toda dimensão com nota < 60 contribui com
   uma recomendação adicional ligada ao seu rationale.

Cada recomendação cai em uma de três colunas na UI:

* **Fazer agora** — resolver esta semana
* **Em seguida** — entra no próximo sprint
* **Depois** — valioso, mas não bloqueia

---

## 4. Plano de execução

`scoring/plan.py` transforma o conjunto de recomendações em cinco fases:

| # | Fase                                | Por que vem primeiro |
|---|-------------------------------------|----------------------|
| 1 | Estabilizar higiene do repositório  | Tapa vazamentos de segredo e precipícios de higiene |
| 2 | Estabelecer portões de qualidade    | CI + lint + testes criam o loop de feedback que o trabalho futuro depende |
| 3 | Arquitetura & Manutenibilidade      | Modela o código uma vez que a rede de segurança existe |
| 4 | Documentação & onboarding           | Codifica o que o time agora sabe |
| 5 | Pronto para release                 | Dockerfile, runbooks, changelog, versionamento |

Cada fase carrega chips de risco / esforço / impacto e uma lista de itens
concretos tirados do conjunto de problemas + recomendações.

---

## 5. Faixas de nota

```
A   geral ≥ 90
B   geral ≥ 80
C   geral ≥ 70
D   geral ≥ 60
F   caso contrário
```

O chip de nível de risco no hero do sumário usa uma faixa levemente diferente
para comunicar urgência operacional em vez de um boletim:

| Geral   | Risco    |
|---------|----------|
| < 50    | Alto     |
| 50–69   | Médio    |
| 70–84   | Baixo    |
| ≥ 85    | Mínimo   |

---

## 6. Exemplo comentado — o demo embutido

`samples/demo-repo` é feito para acionar todos os caminhos críticos.

**Observações que o scanner registra:**

* README fino sem seção de setup.
* Sem `docs/`, sem LICENSE, sem CHANGELOG, sem CONTRIBUTING.
* Sem testes em lugar algum. Sem CI. Sem Dockerfile. Sem lint / formatter.
* Um arquivo `.env` commitado.
* Um artefato `build/bundle.js` commitado.
* Apenas `node_modules/` no `.gitignore` (sem env, sem artefatos).

**Notas esperadas por dimensão** (aproximadas — determinísticas por scan):

| Dimensão               | Nota |
|------------------------|:----:|
| Documentação           |  ~15 |
| Testes                 |   5  |
| Arquitetura            |  ~70 |
| Entrega & DevEx        |  ~30 |
| Manutenibilidade       |  ~65 |
| Higiene de Segurança   |  ~25 |
| Limpeza do Repositório |  ~60 |

**Headline esperada:** geral ≈ **46**, nota **F**, **13 problemas**,
**26 recomendações**, **5 fases**, **4 documentos gerados**.

Rodar `POST /api/analyze/demo` contra um backend fresco reproduz esses números
exatamente.

---

## 7. Estendendo o engine de scoring

Adicionar um novo sinal costuma ser uma mudança em 3 arquivos:

1. **`analyzer/scanner.py`** — registrar o novo contador / lista no
   `ScanResult`.
2. **`scoring/dimensions.py`** — consumir na dimensão relevante com um delta
   pequeno e uma string correspondente de positivo / preocupação /
   recomendação.
3. **`scoring/issues.py`** — emitir um problema quando o sinal é forte o
   bastante para merecer o board de problemas.

Em seguida, adicionar um teste em `apps/api/tests/test_analyzer.py` que monta
uma fixture onde o novo sinal está presente e afirma que o ID do problema
esperado aparece.

Manter as heurísticas pequenas e legíveis. A camada inteira de scoring caber
numa leitura de cabo a rabo é uma feature; não transformar em um rule engine
de 2.000 linhas sem um motivo real.
