# ForgeOps API

FastAPI service that powers ForgeOps repository analysis. Reads a ZIP upload
or the seeded demo repo, scans the tree, runs the scoring engine, emits
issues / recommendations / a phased plan, and generates markdown reports.

## Quick start

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn forgeops.main:app --reload --port 8000
```

## Endpoints

| Method | Path                                 | Purpose                                   |
|--------|--------------------------------------|-------------------------------------------|
| GET    | `/health`                            | Liveness probe                            |
| POST   | `/api/analyze/upload`                | Analyze an uploaded ZIP                   |
| POST   | `/api/analyze/demo`                  | Analyze the bundled demo repository       |
| GET    | `/api/analysis/{id}`                 | Fetch an analysis session                 |
| GET    | `/api/analysis/{id}/documents`       | Fetch the generated markdown docs         |
| GET    | `/api/analysis`                      | List recent analyses                      |

The full data model lives in `forgeops/models/schemas.py`. See the root
`docs/SCORING.md` for a reference of how scores and issues are computed.
