"""Monta um plano de execução em fases a partir de issues + pontos fracos das dimensões."""

from __future__ import annotations

from ..models.schemas import IssueItem, PlanPhase, PlanTask
from .dimensions import DimensionResult


def _tasks_for_issues(issues: list[IssueItem], ids: list[str]) -> list[PlanTask]:
    tasks: list[PlanTask] = []
    idset = set(ids)
    for issue in issues:
        if issue.id not in idset:
            continue
        effort = {
            "low": "S",
            "medium": "M",
            "high": "M",
            "critical": "L",
        }.get(issue.severity, "M")
        tasks.append(PlanTask(
            title=issue.title,
            detail=issue.recommendation,
            effort=effort,  # type: ignore[arg-type]
        ))
    return tasks


def _fallback(tasks: list[PlanTask], fallback: list[PlanTask]) -> list[PlanTask]:
    return tasks if tasks else fallback


def build_plan(issues: list[IssueItem], dims: list[DimensionResult]) -> list[PlanPhase]:
    issue_ids = {i.id for i in issues}
    sev_count = {
        "critical": sum(1 for i in issues if i.severity == "critical"),
        "high": sum(1 for i in issues if i.severity == "high"),
    }

    # Fase 1 — Estabilizar higiene do repo
    phase1_ids = [
        "security.env_committed",
        "security.secret_like_files",
        "hygiene.no_gitignore",
        "hygiene.node_modules_committed",
        "hygiene.build_artifacts",
        "config.no_env_example",
        "legal.license.missing",
    ]
    phase1_tasks = _tasks_for_issues(issues, phase1_ids)
    phase1_tasks = _fallback(phase1_tasks, [
        PlanTask(
            title="Auditar .gitignore e artefatos commitados",
            detail="Confirmar que nenhum segredo, saída de build ou pasta de dependências está versionada.",
            effort="S",
        ),
    ])

    # Fase 2 — Portões de qualidade
    phase2_ids = [
        "testing.none",
        "testing.thin",
        "testing.no_runner",
        "ci.missing",
        "quality.no_lint",
        "quality.no_formatter",
    ]
    phase2_tasks = _tasks_for_issues(issues, phase2_ids)
    phase2_tasks = _fallback(phase2_tasks, [
        PlanTask(
            title="Reforçar portões de qualidade",
            detail="Adicionar configs de lint + formatter e conectá-las ao CI junto com os testes.",
            effort="M",
        ),
    ])

    # Fase 3 — Limpeza de arquitetura
    low_arch = next((d for d in dims if d.key == "architecture"), None)
    low_maint = next((d for d in dims if d.key == "maintainability"), None)
    phase3_tasks: list[PlanTask] = []
    if "architecture.deep_tree" in issue_ids:
        phase3_tasks.extend(_tasks_for_issues(issues, ["architecture.deep_tree"]))
    if low_arch and low_arch.score < 70:
        for r in low_arch.recommendations[:2]:
            phase3_tasks.append(PlanTask(title=r, detail=low_arch.rationale, effort="M"))
    if low_maint and low_maint.score < 70:
        for r in low_maint.recommendations[:2]:
            phase3_tasks.append(PlanTask(title=r, detail=low_maint.rationale, effort="M"))
    phase3_tasks = _fallback(phase3_tasks, [
        PlanTask(
            title="Revisar fronteiras de módulos",
            detail="Confirmar que cada pasta de topo tem uma responsabilidade única e bem definida.",
            effort="M",
        ),
    ])

    # Fase 4 — Documentação & onboarding
    phase4_ids = [
        "docs.readme.missing",
        "docs.readme.thin",
        "docs.readme.no_setup",
        "docs.folder.missing",
        "docs.contributing.missing",
        "docs.changelog.missing",
        "delivery.no_docker",
    ]
    phase4_tasks = _tasks_for_issues(issues, phase4_ids)
    phase4_tasks = _fallback(phase4_tasks, [
        PlanTask(
            title="Escrever docs de arquitetura e onboarding",
            detail="Criar docs/ARCHITECTURE.md e docs/ONBOARDING.md para encurtar o tempo até o primeiro PR.",
            effort="M",
        ),
    ])

    # Fase 5 — Pronto para release
    phase5_tasks = [
        PlanTask(
            title="Definir processo de release",
            detail="Documente versionamento, branching de release e publicação em RELEASE.md.",
            effort="M",
        ),
        PlanTask(
            title="Expor endpoints de health e readiness",
            detail="Para serviços backend, exponha /health e /ready com status estruturado.",
            effort="S",
        ),
        PlanTask(
            title="Publicar fluxo de changelog",
            detail="Adote keep-a-changelog e linke releases a partir do README.",
            effort="S",
        ),
    ]

    risk_of_p1 = "high" if sev_count["critical"] or sev_count["high"] >= 2 else "medium" if sev_count["high"] else "low"

    return [
        PlanPhase(
            phase=1,
            title="Estabilizar higiene do repositório",
            goal="Eliminar segredos commitados, artefatos e lacunas básicas de higiene.",
            impact="high",
            effort="small",
            risk=risk_of_p1,  # type: ignore[arg-type]
            tasks=phase1_tasks,
        ),
        PlanPhase(
            phase=2,
            title="Estabelecer portões de qualidade",
            goal="Fazer cada PR rodar lint + testes no CI.",
            impact="high",
            effort="medium",
            risk="medium",
            tasks=phase2_tasks,
        ),
        PlanPhase(
            phase=3,
            title="Arquitetura & Manutenibilidade",
            goal="Apertar fronteiras de módulos e reduzir dívida estrutural.",
            impact="medium",
            effort="medium",
            risk="medium",
            tasks=phase3_tasks,
        ),
        PlanPhase(
            phase=4,
            title="Documentação & onboarding",
            goal="Tornar o projeto agradável para um novo colaborador em 30 minutos.",
            impact="high",
            effort="medium",
            risk="low",
            tasks=phase4_tasks,
        ),
        PlanPhase(
            phase=5,
            title="Pronto para release",
            goal="Entregar com confiança: processo de release, health checks e changelog.",
            impact="medium",
            effort="medium",
            risk="low",
            tasks=phase5_tasks,
        ),
    ]
