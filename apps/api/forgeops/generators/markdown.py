"""Gera quatro relatórios em markdown a partir dos fatos da análise.

O texto é determinístico, mas referencia achados reais (ex.: "sem CI detectado"),
para soar como uma auditoria ancorada em evidências, não texto genérico.
"""

from __future__ import annotations

from datetime import datetime, timezone
from textwrap import dedent


def _now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

from ..models.schemas import (
    AnalysisSummary,
    DetectedStack,
    GeneratedDocument,
    IssueItem,
    PlanPhase,
    RecommendationItem,
    RepositoryStats,
    ScoreDimension,
)


_RISK_LABEL = {"low": "BAIXO", "medium": "MÉDIO", "high": "ALTO"}
_PRIORITY_LABEL = {"now": "Fazer agora", "next": "Fazer em seguida", "later": "Fazer depois"}
_IMPACT_LABEL = {"low": "baixo", "medium": "médio", "high": "alto"}
_EFFORT_LABEL_PT = {"small": "pequeno", "medium": "médio", "large": "grande"}


def _bullets(items: list[str]) -> str:
    if not items:
        return "- _Nada detectado._\n"
    return "\n".join(f"- {x}" for x in items) + "\n"


def _severity_icon(sev: str) -> str:
    return {"critical": "[CRIT]", "high": "[ALTO]", "medium": "[MÉD] ", "low": "[BAIXO]"}.get(sev, "[---]")


def _format_score_table(scores: list[ScoreDimension]) -> str:
    lines = ["| Dimensão | Nota | Peso |", "| --- | ---: | ---: |"]
    for s in scores:
        lines.append(f"| {s.name} | **{s.score}/100** | {int(s.weight*100)}% |")
    return "\n".join(lines)


def _gen_overview(
    repo_name: str,
    summary: AnalysisSummary,
    stats: RepositoryStats,
    stack: DetectedStack,
    scores: list[ScoreDimension],
) -> GeneratedDocument:
    top_types = ", ".join(f"{t.extension} ({t.files})" for t in stats.file_type_breakdown[:5]) or "—"
    top_langs = ", ".join(
        f"{l.language} ({int(l.share*100)}%)" for l in stats.language_breakdown[:5]
    ) or "—"

    content = dedent(f"""
    # Visão geral do repositório — {repo_name}

    _Gerado pelo ForgeOps em {_now_utc_str()} UTC_

    ## Síntese
    {summary.headline}

    **Nota geral:** {summary.overall_score}/100 ({summary.grade})
    **Nível de risco:** {_RISK_LABEL.get(summary.risk_level, summary.risk_level.upper())}

    ## Num relance
    - **Arquivos:** {stats.total_files}
    - **Diretórios:** {stats.total_directories}
    - **Tamanho total:** {stats.total_size_bytes / 1024:.1f} KB
    - **Arquivos de código:** {stats.code_files}
    - **Profundidade máxima:** {stats.max_depth}
    - **Tipo de projeto inferido:** {stack.inferred_project_type}

    ## Stack detectada
    - **Linguagens primárias:** {", ".join(stack.primary_languages) or "—"}
    - **Frontend:** {", ".join(stack.probable_frontend) or "—"}
    - **Backend:** {", ".join(stack.probable_backend) or "—"}
    - **Frameworks:** {", ".join(stack.frameworks) or "—"}
    - **Bancos de dados:** {", ".join(stack.databases) or "—"}
    - **Testes:** {", ".join(stack.testing_tools) or "—"}
    - **Ferramentas de CI:** {", ".join(stack.ci_tools) or "—"}
    - **Containerização:** {", ".join(stack.containerization) or "—"}
    - **Gerenciadores de pacotes:** {", ".join(stack.package_managers) or "—"}

    ## Composição
    - **Top tipos de arquivo:** {top_types}
    - **Top linguagens por tamanho:** {top_langs}

    ## Resumo das notas
    {_format_score_table(scores)}

    ## Pontos fortes
    {_bullets(summary.strengths)}
    ## Pontos frágeis
    {_bullets(summary.weaknesses)}
    """).strip() + "\n"

    return GeneratedDocument(slug="repository-overview", title="Visão geral do repositório", content=content)


def _gen_architecture(
    repo_name: str,
    stats: RepositoryStats,
    stack: DetectedStack,
    scores: list[ScoreDimension],
) -> GeneratedDocument:
    arch = next((s for s in scores if s.key == "architecture"), None)
    maint = next((s for s in scores if s.key == "maintainability"), None)

    def _dim_section(s: ScoreDimension | None) -> str:
        if not s:
            return ""
        return dedent(f"""
        ### {s.name} — {s.score}/100
        {s.rationale}

        **Pontos positivos**
        {_bullets(s.positives)}
        **Preocupações**
        {_bullets(s.concerns)}
        **Recomendações**
        {_bullets(s.recommendations)}
        """).strip()

    content = dedent(f"""
    # Revisão de arquitetura — {repo_name}

    _Gerado pelo ForgeOps em {_now_utc_str()} UTC_

    Esta revisão observa o formato do repositório: como ele está organizado,
    como as principais preocupações estão separadas e o quanto a stack detectada
    está alinhada com a estrutura do projeto.

    ## Formato do projeto
    - **Tipo de projeto inferido:** {stack.inferred_project_type}
    - **Linguagens primárias:** {", ".join(stack.primary_languages) or "—"}
    - **Profundidade máxima de diretórios:** {stats.max_depth}
    - **Total de diretórios:** {stats.total_directories}
    - **Arquivos de código / total:** {stats.code_files} / {stats.total_files}

    ## Alinhamento da stack
    - **Sinais de frontend:** {", ".join(stack.probable_frontend) or "—"}
    - **Sinais de backend:** {", ".join(stack.probable_backend) or "—"}
    - **Frameworks:** {", ".join(stack.frameworks) or "—"}

    {_dim_section(arch)}

    {_dim_section(maint)}
    """).strip() + "\n"

    return GeneratedDocument(slug="architecture-review", title="Revisão de arquitetura", content=content)


def _gen_debt(
    repo_name: str,
    issues: list[IssueItem],
    scores: list[ScoreDimension],
) -> GeneratedDocument:
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ordered = sorted(issues, key=lambda i: (severity_rank.get(i.severity, 4), i.category))

    by_category: dict[str, list[IssueItem]] = {}
    for issue in ordered:
        by_category.setdefault(issue.category, []).append(issue)

    sections = []
    for cat, items in by_category.items():
        block = [f"### {cat}"]
        for issue in items:
            block.append(f"#### {_severity_icon(issue.severity)} {issue.title}")
            block.append(issue.description)
            block.append("")
            if issue.evidence:
                block.append("**Evidências**")
                block.extend(f"- {e}" for e in issue.evidence)
                block.append("")
            block.append(f"**Recomendação:** {issue.recommendation}")
            block.append("")
        sections.append("\n".join(block))

    dim_table = _format_score_table(scores)

    content = dedent(f"""
    # Relatório de dívida técnica — {repo_name}

    _Gerado pelo ForgeOps em {_now_utc_str()} UTC_

    Este relatório consolida os problemas detectados nas dimensões de higiene,
    qualidade, testes, documentação, entrega e arquitetura. A severidade reflete
    o provável impacto; o ForgeOps aponta problemas de forma conservadora,
    baseando-se apenas em evidências observáveis.

    ## Notas por dimensão
    {dim_table}

    ## Problemas

    """).strip() + "\n\n"

    content += ("\n\n".join(sections) if sections else "_Nenhum problema detectado._\n")
    return GeneratedDocument(slug="technical-debt-report", title="Relatório de dívida técnica", content=content)


def _gen_action_plan(
    repo_name: str,
    phases: list[PlanPhase],
    recommendations: list[RecommendationItem],
) -> GeneratedDocument:
    buckets: dict[str, list[RecommendationItem]] = {"now": [], "next": [], "later": []}
    for r in recommendations:
        buckets.setdefault(r.priority, []).append(r)

    def _phase_block(p: PlanPhase) -> str:
        tasks = "\n".join(f"- [{t.effort}] {t.title} — {t.detail}" for t in p.tasks) or "- _Nenhuma tarefa na fila._"
        return dedent(f"""
        ### Fase {p.phase}: {p.title}
        **Objetivo:** {p.goal}

        **Impacto:** {_IMPACT_LABEL.get(p.impact, p.impact)} · **Esforço:** {_EFFORT_LABEL_PT.get(p.effort, p.effort)} · **Risco:** {_IMPACT_LABEL.get(p.risk, p.risk)}

        {tasks}
        """).strip()

    def _rec_block(priority: str, items: list[RecommendationItem]) -> str:
        label = _PRIORITY_LABEL.get(priority, priority)
        if not items:
            return f"### {label}\n- _Nada._\n"
        rows = "\n".join(
            f"- **{r.title}** (impacto {_IMPACT_LABEL.get(r.impact, r.impact)} · esforço {_EFFORT_LABEL_PT.get(r.effort, r.effort)}) — {r.rationale}"
            for r in items
        )
        return f"### {label}\n{rows}\n"

    phase_text = "\n\n".join(_phase_block(p) for p in phases)

    content = dedent(f"""
    # Plano de ação — {repo_name}

    _Gerado pelo ForgeOps em {_now_utc_str()} UTC_

    Um roteiro em fases para elevar este repositório a um nível de portfólio.
    As fases estão ordenadas para que vitórias iniciais destravem o trabalho seguinte.

    ## Execução em fases

    {phase_text}

    ## Recomendações priorizadas

    {_rec_block("now", buckets.get("now", []))}
    {_rec_block("next", buckets.get("next", []))}
    {_rec_block("later", buckets.get("later", []))}
    """).strip() + "\n"

    return GeneratedDocument(slug="action-plan", title="Plano de ação", content=content)


def generate_documents(
    *,
    repo_name: str,
    summary: AnalysisSummary,
    stats: RepositoryStats,
    stack: DetectedStack,
    scores: list[ScoreDimension],
    issues: list[IssueItem],
    recommendations: list[RecommendationItem],
    phases: list[PlanPhase],
) -> list[GeneratedDocument]:
    return [
        _gen_overview(repo_name, summary, stats, stack, scores),
        _gen_architecture(repo_name, stats, stack, scores),
        _gen_debt(repo_name, issues, scores),
        _gen_action_plan(repo_name, phases, recommendations),
    ]
