"""Calcula as 7 dimensões de nota a partir dos fatos de scanner + stack.

Cada variação de pontos é atribuível a uma heurística específica, para que
a explicação "como isso foi calculado" se mantenha honesta.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..analyzer.frameworks import StackDetection
from ..analyzer.scanner import ScanResult


@dataclass
class DimensionResult:
    key: str
    name: str
    score: int
    weight: float
    rationale: str
    positives: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def _clamp(x: float, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(round(x))))


def _readme_quality_points(scan: ScanResult) -> tuple[int, list[str], list[str]]:
    """Retorna (pontos 0-30, positivos, preocupações) com base no conteúdo do README."""
    pos: list[str] = []
    con: list[str] = []
    readme = scan.manifests.get("readme.md") or scan.manifests.get("readme")
    if not readme:
        con.append("Nenhum README encontrado na raiz do repositório.")
        return 0, pos, con

    lower = readme.lower()
    length = len(readme)
    pts = 0
    if length > 200:
        pts += 6
        pos.append("README presente e com conteúdo consistente.")
    else:
        con.append("README existe, mas é muito curto (< 200 caracteres).")
    if any(k in lower for k in ("## install", "## setup", "## getting started", "installation", "quickstart", "quick start", "## instalação", "instalação")):
        pts += 6
        pos.append("README traz instruções de instalação ou setup.")
    else:
        con.append("README não tem uma seção clara de setup ou instalação.")
    if any(k in lower for k in ("## usage", "usage", "## example", "example", "## uso", "uso", "exemplo")):
        pts += 5
        pos.append("README traz exemplos ou instruções de uso.")
    else:
        con.append("README não traz exemplos nem instruções de uso.")
    if any(k in lower for k in ("## architecture", "## overview", "features", "## features", "## arquitetura", "## visão geral")):
        pts += 4
        pos.append("README cobre funcionalidades ou arquitetura.")
    if "```" in readme:
        pts += 3
        pos.append("README inclui blocos de código acionáveis.")
    if length > 1500:
        pts += 4
    if any(k in lower for k in ("license", "licença", "mit", "apache")):
        pts += 2
    return min(pts, 30), pos, con


def score_documentation(scan: ScanResult) -> DimensionResult:
    base = 0
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []

    readme_pts, r_pos, r_con = _readme_quality_points(scan)
    base += readme_pts
    positives.extend(r_pos)
    concerns.extend(r_con)
    if not scan.readme_files:
        recs.append("Adicione um README.md com propósito, setup, uso e arquitetura.")

    if scan.docs_files:
        base += 20
        positives.append(f"Detectados {len(scan.docs_files)} arquivos de documentação dedicados.")
    else:
        concerns.append("Nenhum arquivo de documentação dedicado encontrado.")
        recs.append("Crie uma pasta docs/ com notas de arquitetura e onboarding.")

    if scan.changelog_files:
        base += 6
        positives.append("CHANGELOG mantido.")
    else:
        concerns.append("Nenhum CHANGELOG detectado.")
        recs.append("Crie um CHANGELOG.md (formato keep-a-changelog) para registrar releases.")
    if scan.contributing_files:
        base += 6
        positives.append("Guia de contribuição (CONTRIBUTING) presente.")
    else:
        concerns.append("Nenhum guia de contribuição presente.")
    if scan.codeowners_files:
        base += 6
        positives.append("Arquivo CODEOWNERS presente.")

    if scan.license_files:
        base += 12
        positives.append("Arquivo LICENSE presente.")
    else:
        concerns.append("Nenhum arquivo LICENSE no repositório.")
        recs.append("Escolha e commite uma LICENSE (MIT / Apache-2.0 são padrões comuns).")

    env_has_example = any(f.lower().endswith(".example") or "example" in f.lower() for f in scan.env_files)
    if env_has_example:
        base += 10
        positives.append(".env.example documenta a configuração necessária.")
    else:
        concerns.append("Nenhum .env.example para documentar variáveis de ambiente necessárias.")
        recs.append("Commite um .env.example listando todas as variáveis com placeholders seguros.")

    if any("architecture" in d.lower() or "arquitetura" in d.lower() for d in scan.docs_files):
        base += 5
    if any("api" in d.lower() for d in scan.docs_files):
        base += 5

    return DimensionResult(
        key="documentation",
        name="Documentação",
        score=_clamp(base),
        weight=0.18,
        rationale="Avaliado pela profundidade do README, documentação dedicada, changelog, guia de contribuição e presença de .env.example.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def score_testing(scan: ScanResult, stack: StackDetection) -> DimensionResult:
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []

    code_files = max(scan.code_files, 1)
    test_files = len(scan.test_files)
    ratio = test_files / code_files

    base = 0
    if test_files == 0:
        concerns.append("Nenhum arquivo de teste detectado no repositório.")
        recs.append("Adicione uma pasta tests/ e ao menos testes de fumaça para os módulos principais.")
        base = 5
    else:
        if ratio >= 0.25:
            base = 72
            positives.append(f"Cobertura de testes saudável por contagem de arquivos (≈ {ratio:.0%} do código é teste).")
        elif ratio >= 0.10:
            base = 55
            positives.append(f"Alguma cobertura de testes ({test_files} arquivos de teste).")
        elif ratio >= 0.03:
            base = 35
            concerns.append(f"Cobertura de testes rasa ({test_files} testes para {code_files} arquivos de código).")
            recs.append("Expanda testes nos fluxos críticos; vá além de testes de fumaça.")
        else:
            base = 20
            concerns.append(f"Cobertura de testes muito rasa ({test_files} testes para {code_files} arquivos de código).")
            recs.append("Invista em testes unitários nos módulos de maior risco primeiro.")

    if stack.testing_tools:
        base += 15
        positives.append(f"Ferramentas de teste detectadas: {', '.join(stack.testing_tools)}.")
    else:
        concerns.append("Nenhum framework de teste reconhecido nas dependências.")
        recs.append("Adote um test runner padrão (pytest, Jest, Vitest, Go test) para tornar os testes descobríveis.")

    if any("playwright" in t.lower() or "cypress" in t.lower() for t in stack.testing_tools):
        base += 8
        positives.append("Framework de testes end-to-end configurado.")

    return DimensionResult(
        key="testing",
        name="Testes",
        score=_clamp(base),
        weight=0.18,
        rationale="Baseado nos arquivos de teste detectados, sua proporção em relação ao código e as ferramentas de teste encontradas nos manifestos.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def score_delivery(scan: ScanResult, stack: StackDetection) -> DimensionResult:
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []
    base = 30

    if stack.ci_tools:
        base += 30
        positives.append(f"CI configurado: {', '.join(stack.ci_tools)}.")
    else:
        concerns.append("Nenhum workflow de CI detectado.")
        recs.append("Configure GitHub Actions (ou equivalente) para rodar lint + testes em cada PR.")

    if stack.containerization:
        base += 20
        positives.append(f"Containerização presente: {', '.join(stack.containerization)}.")
    else:
        concerns.append("Nenhum Dockerfile ou arquivo compose encontrado.")
        recs.append("Adicione um Dockerfile e docker-compose para execuções locais reproduzíveis.")

    config_names = {c.lower() for c in scan.config_files}
    has_lint = any(n.startswith(".eslintrc") or n in {"ruff.toml", ".ruff.toml"} for n in config_names) or any(
        "eslint" in c.lower() or "ruff" in c.lower() or "flake8" in c.lower() for c in scan.config_files
    )
    has_format = any("prettier" in c.lower() for c in scan.config_files) or any(
        "tool.black" in (scan.manifests.get(m, "")) for m in ("pyproject.toml",)
    )
    if has_lint:
        base += 10
        positives.append("Configuração de lint presente.")
    else:
        concerns.append("Nenhuma configuração de lint detectada.")
        recs.append("Adicione uma config de lint (ESLint / Ruff / golangci-lint) e rode-a no CI.")
    if has_format:
        base += 10
        positives.append("Configuração de formatter presente.")
    else:
        concerns.append("Nenhuma configuração de formatter detectada.")
        recs.append("Adote um formatter (Prettier / Black) e padronize no CI.")

    return DimensionResult(
        key="delivery",
        name="Entrega & DevEx",
        score=_clamp(base),
        weight=0.15,
        rationale="Observa CI, containerização, lint e configuração de formatter.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def score_architecture(scan: ScanResult, stack: StackDetection) -> DimensionResult:
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []
    base = 55

    top = {t.lower() for t in scan.top_level_dirs}
    separated = any(t in top for t in ("frontend", "web", "client")) and any(
        t in top for t in ("backend", "api", "server")
    )
    monorepo_like = "apps" in top or "packages" in top

    if separated or monorepo_like:
        base += 15
        positives.append("Frontend e backend vivem em pastas de topo separadas.")
    else:
        concerns.append("Frontend e backend não estão claramente separados.")
        recs.append("Extraia frontend e backend para pastas ou workspaces dedicados no topo.")

    if stack.inferred_project_type != "Unknown":
        base += 5
        positives.append(f"O formato do projeto é identificável: {stack.inferred_project_type}.")

    if scan.max_depth > 12:
        base -= 8
        concerns.append(f"Estrutura de diretórios muito profunda (profundidade {scan.max_depth}).")
        recs.append("Achate pastas muito aninhadas; busque manter abaixo de 8 níveis quando possível.")
    elif scan.max_depth > 8:
        base -= 4
        concerns.append(f"Estrutura de diretórios um pouco profunda (profundidade {scan.max_depth}).")

    if scan.total_directories > 0 and scan.total_files / max(scan.total_directories, 1) < 1.5 and scan.total_files > 30:
        base -= 4
        concerns.append("Muitas pastas pequenas em relação aos arquivos — possível aninhamento excessivo.")

    if stack.primary_languages and stack.frameworks:
        base += 8
        positives.append(f"Linguagens primárias casam com os frameworks detectados: {', '.join(stack.frameworks[:3])}.")

    if scan.codeowners_files:
        base += 5
        positives.append("Fronteiras de propriedade declaradas via CODEOWNERS.")

    return DimensionResult(
        key="architecture",
        name="Arquitetura",
        score=_clamp(base),
        weight=0.15,
        rationale="Derivado do layout de topo, coerência da stack detectada, profundidade de pastas e marcadores de propriedade.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def score_maintainability(scan: ScanResult) -> DimensionResult:
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []
    base = 60

    if scan.total_files:
        code_share = scan.code_files / scan.total_files
        if code_share >= 0.4:
            base += 8
            positives.append(f"Proporção saudável de arquivos de código ({code_share:.0%} do total).")
        elif code_share < 0.15:
            base -= 6
            concerns.append(f"Baixa proporção de arquivos de código ({code_share:.0%}); o repo pode estar dominado por assets.")

    if scan.total_files and scan.binary_files / scan.total_files > 0.3:
        base -= 10
        concerns.append("Assets binários passam de 30% dos arquivos; considere armazenamento separado ou Git LFS.")
        recs.append("Mova mídia grande ou binários para Git LFS ou um bucket de assets.")

    if len(scan.large_files) > 3:
        base -= 6
        concerns.append(f"{len(scan.large_files)} arquivos maiores que 1 MB.")
        recs.append("Audite arquivos grandes; remova artefatos gerados e commite apenas lockfiles.")

    if len(scan.config_files) >= 4:
        base += 6
        positives.append("Múltiplos arquivos de configuração detectados (lint, formatter, build).")

    if len(scan.top_level_dirs) > 14:
        base -= 4
        concerns.append(f"{len(scan.top_level_dirs)} pastas no topo — considere consolidar.")
        recs.append("Consolide as pastas de topo num layout apps/ ou packages/.")

    if any(f.lower().endswith(("lock", ".lock", "lock.json", "lock.yaml", "lockb")) for f in scan.dependency_files):
        base += 6
        positives.append("Lockfile de dependências commitado (builds reproduzíveis).")
    else:
        concerns.append("Nenhum lockfile de dependências detectado.")
        recs.append("Commite um lockfile (package-lock.json / poetry.lock / go.sum) para builds reproduzíveis.")

    return DimensionResult(
        key="maintainability",
        name="Manutenibilidade",
        score=_clamp(base),
        weight=0.14,
        rationale="Combina composição código/assets, higiene de arquivos grandes, densidade de configs e presença de lockfile.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def score_security(scan: ScanResult) -> DimensionResult:
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []
    base = 80

    if scan.suspicious_files:
        base -= min(len(scan.suspicious_files) * 15, 55)
        for f in scan.suspicious_files[:5]:
            concerns.append(f"Arquivo potencialmente sensível commitado: {f}.")
        recs.append("Tire segredos do repositório; rotacione qualquer credencial que tenha sido commitada.")
    else:
        positives.append("Nenhum arquivo óbvio de segredos no repositório.")

    env_names = [f.lower() for f in scan.env_files]
    real_env = any(name.endswith(".env") or name.endswith("/.env") or name == ".env" for name in env_names)
    example_env = any("example" in n or "sample" in n or "template" in n for n in env_names)
    if real_env and not example_env:
        base -= 20
        concerns.append("Há um .env bruto commitado sem uma versão de exemplo sanitizada.")
        recs.append("Remova o .env commitado e substitua por .env.example; adicione .env ao .gitignore.")
    elif example_env and not real_env:
        base += 8
        positives.append(".env.example presente sem um .env real commitado.")

    if ".gitignore" in {c.lower() for c in scan.config_files}:
        base += 4
        positives.append(".gitignore presente.")
    else:
        concerns.append("Nenhum .gitignore detectado — fonte comum de vazamento acidental de segredos.")
        recs.append("Adicione um .gitignore excluindo .env, node_modules, artefatos de build e pastas de editor.")

    if scan.container_files:
        base += 3

    return DimensionResult(
        key="security",
        name="Higiene de Segurança",
        score=_clamp(base),
        weight=0.10,
        rationale="Revisa segredos commitados, arquivos .env brutos, presença de .gitignore e marcadores de higiene relacionados.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def score_cleanliness(scan: ScanResult) -> DimensionResult:
    positives: list[str] = []
    concerns: list[str] = []
    recs: list[str] = []
    base = 85

    junk_indicators = [".ds_store", "thumbs.db", "desktop.ini"]
    found_junk = [
        f for (f, _) in scan.file_paths
        if f.split("/")[-1].lower() in junk_indicators
    ]
    if found_junk:
        base -= min(len(found_junk) * 5, 20)
        concerns.append(f"Arquivos de lixo do SO detectados ({len(found_junk)}).")
        recs.append("Ignore artefatos do SO no .gitignore (.DS_Store, Thumbs.db, etc.).")

    top = {t.lower() for t in scan.top_level_dirs}
    if "dist" in top or "build" in top or "out" in top:
        base -= 10
        concerns.append("Diretório de saída de build aparenta estar commitado.")
        recs.append("Ignore dist/, build/ e out/; gere-os no CI em vez de commitar.")

    if "node_modules" in top:
        base -= 25
        concerns.append("node_modules aparenta estar commitado no topo.")

    if len(scan.large_files) >= 5:
        base -= 10
        concerns.append(f"{len(scan.large_files)} arquivos > 1 MB commitados.")

    if scan.total_files == 0:
        base = 0
        concerns.append("Repositório aparenta estar vazio.")
    elif scan.total_files < 4:
        base -= 15
        concerns.append("Repositório incomumente pequeno; pode ser um placeholder.")

    if scan.readme_files and scan.license_files and scan.dependency_files:
        base += 5
        positives.append("README, LICENSE e manifesto de dependências todos presentes.")

    return DimensionResult(
        key="cleanliness",
        name="Limpeza do Repositório",
        score=_clamp(base),
        weight=0.10,
        rationale="Procura lixo commitado, saídas de build, arquivos grandes demais e marcadores básicos de higiene.",
        positives=positives,
        concerns=concerns,
        recommendations=recs,
    )


def compute_scores(scan: ScanResult, stack: StackDetection) -> list[DimensionResult]:
    return [
        score_architecture(scan, stack),
        score_maintainability(scan),
        score_documentation(scan),
        score_testing(scan, stack),
        score_delivery(scan, stack),
        score_security(scan),
        score_cleanliness(scan),
    ]


def overall_score(dims: list[DimensionResult]) -> int:
    weight_sum = sum(d.weight for d in dims) or 1.0
    weighted = sum(d.score * d.weight for d in dims) / weight_sum
    return _clamp(weighted)


def grade_for(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def risk_level_for(score: int, issues_high_count: int) -> str:
    if score < 55 or issues_high_count >= 5:
        return "high"
    if score < 70 or issues_high_count >= 2:
        return "medium"
    return "low"
