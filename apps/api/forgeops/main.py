"""FastAPI application entry point for ForgeOps."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .config import SETTINGS, ensure_dirs


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def create_app() -> FastAPI:
    ensure_dirs()
    app = FastAPI(
        title="ForgeOps API",
        version="0.1.0",
        description=(
            "Motor de análise, pontuação e documentação de repositórios. "
            "Aceita um upload de ZIP ou o repositório demo embutido e "
            "retorna uma AnalysisSession completa."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(SETTINGS.cors_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "forgeops.main:app",
        host=SETTINGS.host,
        port=SETTINGS.port,
        reload=False,
    )
