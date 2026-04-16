"""HTTP routes exposing ForgeOps analyses."""

from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..analyzer import analyze_repository, extract_zip_safely
from ..analyzer.zip_safe import SafeExtractionError
from ..config import SETTINGS, ensure_dirs
from ..models.schemas import AnalysisSession, SourceType
from ..storage import get_store


log = logging.getLogger("forgeops.api")
router = APIRouter()


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "forgeops-api"}


@router.get("/api/analysis")
def list_analyses() -> dict:
    store = get_store()
    return {"items": store.list_recent(limit=50)}


@router.get("/api/analysis/{analysis_id}", response_model=AnalysisSession)
def get_analysis(analysis_id: str) -> AnalysisSession:
    store = get_store()
    session = store.get(analysis_id)
    if not session:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return session


@router.get("/api/analysis/{analysis_id}/documents")
def get_documents(analysis_id: str) -> dict:
    store = get_store()
    session = store.get(analysis_id)
    if not session:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return {
        "id": session.id,
        "repo_name": session.repo_name,
        "documents": [d.model_dump() for d in session.generated_documents],
    }


@router.post("/api/analyze/demo", response_model=AnalysisSession)
def analyze_demo() -> AnalysisSession:
    demo_path = SETTINGS.demo_repo_path
    if not demo_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Repositório demo não encontrado em {demo_path}. "
                   "Verifique se samples/demo-repo está presente no projeto.",
        )
    session_id = _new_id()
    session = analyze_repository(
        session_id=session_id,
        repo_path=demo_path,
        repo_name=demo_path.name,
        source_type=SourceType.demo,
    )
    get_store().save(session)
    return session


@router.post("/api/analyze/upload", response_model=AnalysisSession)
async def analyze_upload(file: UploadFile = File(...)) -> AnalysisSession:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="O upload precisa ser um arquivo .zip.")

    ensure_dirs()
    session_id = _new_id()
    work_dir = SETTINGS.extract_dir / session_id
    work_dir.mkdir(parents=True, exist_ok=True)

    # Stream to a temp file, enforcing size limit
    tmp_zip = work_dir / "upload.zip"
    total = 0
    limit = SETTINGS.max_upload_bytes
    try:
        with open(tmp_zip, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Upload excede o tamanho máximo ({limit} bytes).",
                    )
                out.write(chunk)
    except HTTPException:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise
    except Exception as exc:  # pragma: no cover - defensive
        log.exception("Failed to persist upload")
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail="Falha ao persistir o upload.") from exc

    extract_dir = work_dir / "extracted"
    try:
        root = extract_zip_safely(tmp_zip, extract_dir)
    except SafeExtractionError as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    repo_name = Path(file.filename).stem or root.name or "uploaded-repo"
    try:
        session = analyze_repository(
            session_id=session_id,
            repo_path=root,
            repo_name=repo_name,
            source_type=SourceType.upload,
        )
    finally:
        # The uploaded bytes are no longer needed; keep extracted tree for debugging
        try:
            tmp_zip.unlink(missing_ok=True)
        except OSError:
            pass

    get_store().save(session)
    return session


@router.get("/api/config")
def runtime_config() -> dict:
    """Expose non-sensitive runtime knobs so the UI can show limits, etc."""
    return {
        "max_upload_bytes": SETTINGS.max_upload_bytes,
        "demo_repo_present": SETTINGS.demo_repo_path.exists(),
    }
