"""SQLite-backed persistence for analysis sessions.

Stores the full AnalysisSession as JSON; indexed by id and created_at.
This keeps the schema tiny while the application is heuristic-driven.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import SETTINGS, ensure_dirs
from ..models.schemas import AnalysisSession


class AnalysisStore:
    def __init__(self, db_path: Path) -> None:
        ensure_dirs()
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                  id          TEXT PRIMARY KEY,
                  repo_name   TEXT NOT NULL,
                  source_type TEXT NOT NULL,
                  created_at  TEXT NOT NULL,
                  status      TEXT NOT NULL,
                  overall     INTEGER,
                  grade       TEXT,
                  payload     TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at)"
            )

    def save(self, session: AnalysisSession) -> None:
        payload = session.model_dump_json()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO analyses
                  (id, repo_name, source_type, created_at, status, overall, grade, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.repo_name,
                    session.source_type.value,
                    session.created_at.isoformat(),
                    session.status.value,
                    session.summary.overall_score if session.summary else None,
                    session.summary.grade if session.summary else None,
                    payload,
                ),
            )

    def get(self, session_id: str) -> Optional[AnalysisSession]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM analyses WHERE id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        return AnalysisSession.model_validate_json(row["payload"])

    def list_recent(self, limit: int = 25) -> list[dict]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, repo_name, source_type, created_at, status, overall, grade
                FROM analyses
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


_STORE: Optional[AnalysisStore] = None
_STORE_LOCK = threading.Lock()


def get_store() -> AnalysisStore:
    global _STORE
    with _STORE_LOCK:
        if _STORE is None:
            _STORE = AnalysisStore(SETTINGS.db_path)
    return _STORE
