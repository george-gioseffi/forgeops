"""Transforma issues + dimensões de score em uma lista priorizada de recomendações."""

from __future__ import annotations

from ..models.schemas import IssueItem, RecommendationItem
from .dimensions import DimensionResult


_PRIORITY_FROM_SEVERITY = {
    "critical": "now",
    "high": "now",
    "medium": "next",
    "low": "later",
}

_IMPACT_FROM_SEVERITY = {
    "critical": "high",
    "high": "high",
    "medium": "medium",
    "low": "low",
}

_EFFORT_HINTS = {
    "docs.readme.missing": "small",
    "docs.readme.thin": "small",
    "docs.readme.no_setup": "small",
    "docs.folder.missing": "medium",
    "docs.contributing.missing": "small",
    "docs.changelog.missing": "small",
    "legal.license.missing": "small",
    "testing.none": "large",
    "testing.thin": "large",
    "testing.no_runner": "medium",
    "ci.missing": "medium",
    "delivery.no_docker": "medium",
    "quality.no_lint": "small",
    "quality.no_formatter": "small",
    "security.env_committed": "medium",
    "config.no_env_example": "small",
    "security.secret_like_files": "medium",
    "hygiene.no_gitignore": "small",
    "hygiene.node_modules_committed": "small",
    "hygiene.build_artifacts": "small",
    "hygiene.large_files": "medium",
    "architecture.deep_tree": "large",
}


def build_recommendations(
    issues: list[IssueItem], dims: list[DimensionResult]
) -> list[RecommendationItem]:
    recs: list[RecommendationItem] = []
    seen: set[str] = set()

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_issues = sorted(issues, key=lambda i: severity_rank.get(i.severity, 4))

    for issue in sorted_issues:
        if issue.id in seen:
            continue
        seen.add(issue.id)
        recs.append(RecommendationItem(
            id=f"rec.{issue.id}",
            priority=_PRIORITY_FROM_SEVERITY.get(issue.severity, "later"),  # type: ignore[arg-type]
            title=issue.recommendation,
            rationale=issue.description,
            impact=_IMPACT_FROM_SEVERITY.get(issue.severity, "low"),  # type: ignore[arg-type]
            effort=_EFFORT_HINTS.get(issue.id, "medium"),  # type: ignore[arg-type]
        ))

    # Dimension-level recommendations for low-scoring dimensions where no issue surfaced it
    for dim in dims:
        if dim.score >= 70:
            continue
        for r in dim.recommendations:
            key = f"dim.{dim.key}.{r[:40]}"
            if key in seen:
                continue
            seen.add(key)
            priority = "now" if dim.score < 50 else "next"
            recs.append(RecommendationItem(
                id=key,
                priority=priority,  # type: ignore[arg-type]
                title=r,
                rationale=f"Nota de {dim.name} está em {dim.score}/100 — {dim.rationale}",
                impact="medium",
                effort="medium",
            ))
    return recs
