# ForgeOps API

Serviço FastAPI que alimenta a análise de repositórios do ForgeOps. Lê um ZIP
enviado pelo usuário ou o repositório demo embutido, varre a árvore, roda o
engine de scoring, emite problemas / recomendações / um plano em fases e
gera relatórios em Markdown.

## Começo rápido

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn forgeops.main:app --reload --port 8000
```

## Endpoints

| Método | Path                                 | Função                                    |
|--------|--------------------------------------|-------------------------------------------|
| GET    | `/health`                            | Liveness probe                            |
| POST   | `/api/analyze/upload`                | Analisa um ZIP enviado                    |
| POST   | `/api/analyze/demo`                  | Analisa o repositório demo embutido       |
| GET    | `/api/analysis/{id}`                 | Busca uma sessão de análise               |
| GET    | `/api/analysis/{id}/documents`       | Busca os documentos Markdown gerados      |
| GET    | `/api/analysis`                      | Lista análises recentes                   |

O modelo de dados completo vive em `forgeops/models/schemas.py`. Veja o
`docs/SCORING.md` na raiz para a referência de como notas e problemas são
calculados.
