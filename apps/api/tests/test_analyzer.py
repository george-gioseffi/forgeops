"""Tests for scanner + scoring + orchestrator.

These tests create synthetic repositories in a tempdir and verify that
ForgeOps produces grounded, explainable output (rather than asserting on
exact scores which may drift as heuristics evolve).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from forgeops.analyzer.frameworks import detect_stack
from forgeops.analyzer.orchestrator import analyze_repository
from forgeops.analyzer.scanner import scan_repository
from forgeops.analyzer.zip_safe import extract_zip_safely, SafeExtractionError
from forgeops.models.schemas import SourceType
from forgeops.scoring.dimensions import compute_scores, grade_for, overall_score


def _write(root: Path, relpath: str, content: str = "") -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_clean_repo(root: Path) -> None:
    _write(root, "README.md", "# My Project\n\n## Installation\nRun `pip install`.\n\n## Usage\n```bash\nmyproject\n```\n\n## Features\n- a\n- b\n" * 5)
    _write(root, "LICENSE", "MIT License\n")
    _write(root, ".env.example", "API_KEY=\n")
    _write(root, ".gitignore", "node_modules\n")
    _write(root, "pyproject.toml", '[project]\nname="x"\ndependencies=["fastapi","pytest"]\n')
    _write(root, "Dockerfile", "FROM python:3.12\n")
    _write(root, ".github/workflows/ci.yml", "name: ci\n")
    _write(root, "src/app.py", "def hi():\n    return 1\n")
    _write(root, "tests/test_app.py", "def test_hi():\n    assert True\n")
    _write(root, "docs/ARCHITECTURE.md", "# Architecture\nStuff.\n")
    _write(root, ".prettierrc", "{}\n")
    _write(root, ".eslintrc.json", "{}\n")


def _make_weak_repo(root: Path) -> None:
    _write(root, "index.js", "console.log('hi')")
    _write(root, ".env", "SECRET=abc123\n")
    _write(root, "secrets.json", "{}\n")


def test_safe_extraction_rejects_absolute_and_traversal(tmp_path: Path):
    import zipfile

    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("../evil.txt", "nope")
    with pytest.raises(SafeExtractionError):
        extract_zip_safely(bad, tmp_path / "out")


def test_scanner_categorizes_basic_repo(tmp_path: Path):
    _make_clean_repo(tmp_path)
    scan = scan_repository(tmp_path)
    assert scan.total_files > 0
    assert any("README" in f.upper() for f in scan.readme_files)
    assert scan.license_files
    assert scan.test_files
    assert scan.ci_files
    assert scan.container_files
    assert any(".env.example" in f.lower() for f in scan.env_files)


def test_stack_detection_picks_up_python_and_ci(tmp_path: Path):
    _make_clean_repo(tmp_path)
    scan = scan_repository(tmp_path)
    stack = detect_stack(scan)
    assert "Python" in stack.primary_languages
    assert "FastAPI" in stack.frameworks
    assert "GitHub Actions" in stack.ci_tools
    assert "Docker" in stack.containerization


def test_scores_and_grade_for_clean_repo(tmp_path: Path):
    _make_clean_repo(tmp_path)
    scan = scan_repository(tmp_path)
    stack = detect_stack(scan)
    dims = compute_scores(scan, stack)
    total = overall_score(dims)
    assert total >= 60
    assert grade_for(total) in {"A+", "A", "B", "C"}


def test_weak_repo_triggers_critical_issues(tmp_path: Path):
    _make_weak_repo(tmp_path)
    session = analyze_repository(
        session_id="test1",
        repo_path=tmp_path,
        repo_name="weak",
        source_type=SourceType.upload,
    )
    assert session.status.value == "complete"
    ids = {i.id for i in session.issues}
    assert "security.env_committed" in ids or "security.secret_like_files" in ids
    assert "docs.readme.missing" in ids
    assert "legal.license.missing" in ids
    assert "testing.none" in ids
    assert session.summary is not None
    assert session.summary.risk_level in {"medium", "high"}


def test_documents_are_generated(tmp_path: Path):
    _make_clean_repo(tmp_path)
    session = analyze_repository(
        session_id="test2",
        repo_path=tmp_path,
        repo_name="clean",
        source_type=SourceType.demo,
    )
    slugs = {d.slug for d in session.generated_documents}
    assert "repository-overview" in slugs
    assert "architecture-review" in slugs
    assert "technical-debt-report" in slugs
    assert "action-plan" in slugs
    for doc in session.generated_documents:
        assert len(doc.content) > 100
        assert session.repo_name in doc.content
