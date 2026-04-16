# Build from the repo root so the image can include samples/demo-repo.
# docker-compose passes context: . and dockerfile: apps/api/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FORGEOPS_DATA_DIR=/data \
    FORGEOPS_EXTRACT_DIR=/data/extracted \
    FORGEOPS_DEMO_REPO=/app/samples/demo-repo

WORKDIR /app

COPY apps/api/requirements.txt ./
RUN pip install -r requirements.txt

COPY apps/api/forgeops ./forgeops
COPY samples ./samples

RUN mkdir -p /data/extracted

EXPOSE 8000

CMD ["uvicorn", "forgeops.main:app", "--host", "0.0.0.0", "--port", "8000"]
