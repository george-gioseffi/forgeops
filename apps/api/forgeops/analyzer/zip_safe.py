"""Safe ZIP extraction.

Prevents path traversal (zip-slip), over-sized payloads, and absolute paths.
Only writes files and directories that resolve under the destination root.
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path


class SafeExtractionError(RuntimeError):
    """Raised when a ZIP attempts unsafe extraction."""


DEFAULT_MAX_TOTAL_BYTES = 500 * 1024 * 1024   # 500 MB uncompressed
DEFAULT_MAX_FILES = 20000
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024      # per-file cap


def extract_zip_safely(
    zip_path: Path,
    dest_dir: Path,
    *,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> Path:
    """Extract *zip_path* into *dest_dir* and return the root directory written.

    If the archive has a single top-level folder, that folder is returned;
    otherwise *dest_dir* itself is returned.
    """
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not zipfile.is_zipfile(zip_path):
        raise SafeExtractionError("O arquivo enviado não é um ZIP válido.")

    total_bytes = 0
    top_level: set[str] = set()

    with zipfile.ZipFile(zip_path) as zf:
        members = zf.infolist()
        if len(members) > max_files:
            raise SafeExtractionError(
                f"O arquivo contém entradas demais ({len(members)} > {max_files})."
            )

        for member in members:
            name = member.filename
            if not name or name.endswith("/"):
                # Record directory top-level only
                first = name.strip("/").split("/", 1)[0] if name.strip("/") else ""
                if first:
                    top_level.add(first)
                continue

            # Reject absolute paths and traversal
            normalized = os.path.normpath(name).replace("\\", "/")
            if normalized.startswith("/") or normalized.startswith(".."):
                raise SafeExtractionError(f"Caminho inseguro no arquivo: {name}")
            if ":" in normalized.split("/", 1)[0]:
                raise SafeExtractionError(f"Caminho inseguro no arquivo: {name}")

            target = (dest_dir / normalized).resolve()
            if not str(target).startswith(str(dest_dir)):
                raise SafeExtractionError(f"Caminho escapa do destino: {name}")

            if member.file_size > max_file_size:
                raise SafeExtractionError(
                    f"Arquivo muito grande dentro do ZIP: {name} ({member.file_size} bytes)."
                )
            total_bytes += member.file_size
            if total_bytes > max_total_bytes:
                raise SafeExtractionError(
                    "O ZIP descompactado excede o tamanho permitido."
                )

            top_level.add(normalized.split("/", 1)[0])
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member, "r") as src, open(target, "wb") as dst:
                dst.write(src.read())

    # If archive wrapped everything in one folder, return that folder
    if len(top_level) == 1:
        only = next(iter(top_level))
        candidate = dest_dir / only
        if candidate.is_dir():
            return candidate
    return dest_dir
