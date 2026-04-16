"""End-to-end orchestration: directory → AnalysisSession.

This module does not care how the repository got on disk.
It just takes a path and a repo label and returns a populated session.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..generators.markdown import generate_documents
from ..models.schemas import (
    AnalysisSession,
    AnalysisStatus,
    AnalysisSummary,
    DetectedStack,
    FileTypeBreakdown,
    IssueItem,
    LanguageBreakdown,
    LargestFile,
    RepositoryStats,
    ScoreDimension,
    SourceType,
)
from ..scoring.dimensions import (
    compute_scores,
    grade_for,
    overall_score,
    risk_level_for,
)
from ..scoring.issues import generate_issues
from ..scoring.plan import build_plan
from ..scoring.recommendations import build_recommendations
from .frameworks import detect_stack
from .scanner import (
    ScanResult,
    largest_files,
    scan_repository,
    summarize_file_types,
    summarize_languages,
)


def _build_repo_stats(scan: ScanResult) -> RepositoryStats:
    avg_depth = (
        sum(scan.file_depths) / len(scan.file_depths) if scan.file_depths else 0.0
    )
    file_type_breakdown = [
        FileTypeBreakdown(**row) for row in summarize_file_types(
            scan.extension_files, scan.extension_bytes, top=10
        )
    ]
    language_breakdown = [
        LanguageBreakdown(**row) for row in summarize_languages(
            scan.language_files, scan.language_bytes
        )
    ]
    lf = [LargestFile(**row) for row in largest_files(scan.file_paths, top=10)]
    return RepositoryStats(
        total_files=scan.total_files,
        total_directories=scan.total_directories,
        total_size_bytes=scan.total_size_bytes,
        code_files=scan.code_files,
        code_size_bytes=scan.code_size_bytes,
        max_depth=scan.max_depth,
        avg_depth=round(avg_depth, 2),
        file_type_breakdown=file_type_breakdown,
        language_breakdown=language_breakdown,
        largest_files=lf,
        config_files=scan.config_files,
        docs_files=scan.docs_files,
        test_files=scan.test_files,
        ci_files=scan.ci_files,
        container_files=scan.container_files,
        env_files=scan.env_files,
        dependency_files=scan.dependency_files,
        suspicious_files=scan.suspicious_files,
        large_files_count=len(scan.large_files),
        binary_files_count=scan.binary_files,
    )


def _build_summary(
    dims: list[ScoreDimension], issues: list[IssueItem], stack: DetectedStack
) -> AnalysisSummary:
    total = overall_score(dims) if dims else 0
    grade = grade_for(total)
    high = sum(1 for i in issues if i.severity in ("critical", "high"))
    risk = risk_level_for(total, high)

    strengths: list[str] = []
    weaknesses: list[str] = []
    for d in sorted(dims, key=lambda x: x.score, reverse=True):
        if d.score >= 75 and d.positives:
            strengths.append(f"{d.name}: {d.positives[0]}")
    for d in sorted(dims, key=lambda x: x.score):
        if d.score < 60 and d.concerns:
            weaknesses.append(f"{d.name}: {d.concerns[0]}")

    # Headline: uma frase curta e direta
    project = stack.inferred_project_type if stack.inferred_project_type else "repositório"
    if total >= 80:
        headline = f"Um {project} sólido, com higiene forte e estrutura clara."
    elif total >= 65:
        headline = f"Um {project} razoável, com algumas áreas relevantes para melhorar."
    elif total >= 50:
        headline = f"Um {project} viável, mas com lacunas perceptíveis em higiene, testes e entrega."
    else:
        headline = f"Um {project} pouco desenvolvido, com dívida significativa de qualidade e higiene."

    return AnalysisSummary(
        headline=headline,
        overall_score=total,
        grade=grade,  # type: ignore[arg-type]
        risk_level=risk,  # type: ignore[arg-type]
        strengths=strengths[:5],
        weaknesses=weaknesses[:5],
    )


def analyze_repository(
    *,
    session_id: str,
    repo_path: str | Path,
    repo_name: str,
    source_type: SourceType,
) -> AnalysisSession:
    created_at = datetime.now(timezone.utc).replace(tzinfo=None)
    root = Path(repo_path)

    if not root.exists() or not root.is_dir():
        return AnalysisSession(
            id=session_id,
            source_type=source_type,
            repo_name=repo_name,
            created_at=created_at,
            status=AnalysisStatus.failed,
            error=f"Caminho do repositório não existe: {root}",
        )

    scan = scan_repository(root)
    stack_det = detect_stack(scan)
    stack_model = DetectedStack(**stack_det.__dict__)

    stats = _build_repo_stats(scan)
    dim_results = compute_scores(scan, stack_det)
    scores = [
        ScoreDimension(
            key=d.key,
            name=d.name,
            score=d.score,
            weight=d.weight,
            rationale=d.rationale,
            positives=d.positives,
            concerns=d.concerns,
            recommendations=d.recommendations,
        )
        for d in dim_results
    ]
    issues = generate_issues(scan, stack_det)
    recommendations = build_recommendations(issues, dim_results)
    phases = build_plan(issues, dim_results)
    summary = _build_summary(scores, issues, stack_model)

    documents = generate_documents(
        repo_name=repo_name,
        summary=summary,
        stats=stats,
        stack=stack_model,
        scores=scores,
        issues=issues,
        recommendations=recommendations,
        phases=phases,
    )

    return AnalysisSession(
        id=session_id,
        source_type=source_type,
        repo_name=repo_name,
        created_at=created_at,
        status=AnalysisStatus.complete,
        summary=summary,
        repository_stats=stats,
        detected_stack=stack_model,
        scores=scores,
        issues=issues,
        recommendations=recommendations,
        phases=phases,
        generated_documents=documents,
    )
