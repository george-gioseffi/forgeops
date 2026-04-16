"""Runtime configuration, sourced from environment variables with safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    host: str = os.environ.get("FORGEOPS_API_HOST", "0.0.0.0")
    port: int = _env_int("FORGEOPS_API_PORT", 8000)
    cors_origins: tuple[str, ...] = tuple(
        _env_list(
            "FORGEOPS_CORS_ORIGINS",
            ["http://localhost:3000", "http://127.0.0.1:3000"],
        )
    )
    max_upload_bytes: int = _env_int("FORGEOPS_MAX_UPLOAD_BYTES", 50 * 1024 * 1024)
    data_dir: Path = Path(os.environ.get("FORGEOPS_DATA_DIR", "./data")).resolve()
    extract_dir: Path = Path(
        os.environ.get("FORGEOPS_EXTRACT_DIR", "./data/extracted")
    ).resolve()
    demo_repo_path: Path = Path(
        os.environ.get(
            "FORGEOPS_DEMO_REPO",
            str(Path(__file__).resolve().parents[3] / "samples" / "demo-repo"),
        )
    )

    @property
    def db_path(self) -> Path:
        return self.data_dir / "forgeops.db"


SETTINGS = Settings()


def ensure_dirs() -> None:
    SETTINGS.data_dir.mkdir(parents=True, exist_ok=True)
    SETTINGS.extract_dir.mkdir(parents=True, exist_ok=True)
