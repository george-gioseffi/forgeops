"""Gerador determinístico de problemas.

Cada problema é ancorado numa observação do scanner e carrega uma lista
``evidence`` explícita, para que a UI possa mostrar "foi por isso que isso foi apontado".
"""

from __future__ import annotations

from ..analyzer.frameworks import StackDetection
from ..analyzer.scanner import ScanResult
from ..models.schemas import IssueItem


def _make_issue(
    id_: str,
    *,
    severity: str,
    category: str,
    title: str,
    description: str,
    evidence: list[str],
    recommendation: str,
) -> IssueItem:
    return IssueItem(
        id=id_,
        severity=severity,  # type: ignore[arg-type]
        category=category,
        title=title,
        description=description,
        evidence=evidence,
        recommendation=recommendation,
    )


def generate_issues(scan: ScanResult, stack: StackDetection) -> list[IssueItem]:
    issues: list[IssueItem] = []

    # --- Documentação ---
    if not scan.readme_files:
        issues.append(_make_issue(
            "docs.readme.missing",
            severity="high",
            category="Documentação",
            title="README ausente",
            description="Nenhum README.md foi encontrado na raiz do repositório. Novos colaboradores não têm um ponto de entrada.",
            evidence=["Nenhum README.* na raiz encontrado durante o scan."],
            recommendation="Adicione um README.md cobrindo propósito, setup, uso e contribuições.",
        ))
    else:
        readme = scan.manifests.get("readme.md") or scan.manifests.get("readme", "")
        if len(readme) < 400:
            issues.append(_make_issue(
                "docs.readme.thin",
                severity="medium",
                category="Documentação",
                title="README muito raso",
                description="O README existe, mas tem conteúdo insuficiente.",
                evidence=[f"Tamanho do README: {len(readme)} caracteres."],
                recommendation="Amplie o README com seções de setup, uso e arquitetura.",
            ))
        lower = readme.lower()
        if readme and not any(k in lower for k in ("install", "setup", "getting started", "quickstart", "quick start", "instalação")):
            issues.append(_make_issue(
                "docs.readme.no_setup",
                severity="medium",
                category="Documentação",
                title="README sem instruções de setup",
                description="O README não menciona instalação ou configuração inicial.",
                evidence=["Nenhuma seção 'install', 'setup', 'getting started', 'quickstart' ou 'instalação' encontrada."],
                recommendation="Adicione uma seção 'Começando' com comandos executáveis em copy-paste.",
            ))
    if not scan.docs_files:
        issues.append(_make_issue(
            "docs.folder.missing",
            severity="low",
            category="Documentação",
            title="Sem diretório dedicado de documentação",
            description="O repositório não tem uma pasta docs/ ou arquivos de documentação estruturados.",
            evidence=["Nenhum arquivo markdown dentro de um diretório docs/."],
            recommendation="Crie docs/ com ARCHITECTURE.md e ONBOARDING.md no mínimo.",
        ))
    if not scan.contributing_files:
        issues.append(_make_issue(
            "docs.contributing.missing",
            severity="low",
            category="Documentação",
            title="Sem guia de contribuição",
            description="Colaboradores não têm orientação explícita sobre como propor mudanças.",
            evidence=["Nenhum arquivo CONTRIBUTING.* detectado."],
            recommendation="Adicione CONTRIBUTING.md descrevendo branching, estilo e convenções de PR.",
        ))
    if not scan.changelog_files:
        issues.append(_make_issue(
            "docs.changelog.missing",
            severity="low",
            category="Documentação",
            title="Sem CHANGELOG",
            description="Não há um CHANGELOG rastreando mudanças relevantes entre versões.",
            evidence=["Nenhum arquivo CHANGELOG.* detectado."],
            recommendation="Adote o formato keep-a-changelog e atualize a cada release.",
        ))

    # --- Licenciamento ---
    if not scan.license_files:
        issues.append(_make_issue(
            "legal.license.missing",
            severity="high",
            category="Legal",
            title="Arquivo de licença ausente",
            description="Nenhum arquivo LICENSE foi commitado. Sem licença, o código é, na prática, 'todos os direitos reservados'.",
            evidence=["Nenhum LICENSE / LICENCE encontrado na raiz do repositório."],
            recommendation="Commite uma LICENSE explícita (MIT / Apache-2.0 / BSD são escolhas comuns).",
        ))

    # --- Testes ---
    if not scan.test_files:
        issues.append(_make_issue(
            "testing.none",
            severity="high",
            category="Testes",
            title="Nenhum teste detectado",
            description="Nenhum arquivo de teste foi encontrado em toda a árvore do projeto.",
            evidence=[
                f"Foram varridos {scan.code_files} arquivos de código; 0 arquivos de teste encontrados.",
            ],
            recommendation="Adicione uma pasta tests/ e escreva testes de fumaça para os caminhos mais críticos.",
        ))
    elif scan.code_files and len(scan.test_files) / max(scan.code_files, 1) < 0.05:
        issues.append(_make_issue(
            "testing.thin",
            severity="medium",
            category="Testes",
            title="Cobertura de testes muito rasa",
            description="A proporção de testes em relação aos arquivos de código está abaixo de 5%.",
            evidence=[
                f"{len(scan.test_files)} arquivos de teste contra {scan.code_files} arquivos de código.",
            ],
            recommendation="Amplie a cobertura de testes unitários nos módulos mais críticos.",
        ))
    if not stack.testing_tools:
        issues.append(_make_issue(
            "testing.no_runner",
            severity="medium",
            category="Testes",
            title="Nenhum test runner configurado",
            description="Nenhum framework de teste reconhecido está declarado nos manifestos detectados.",
            evidence=["Sem entradas de pytest / jest / vitest / mocha / cypress / playwright / unittest."],
            recommendation="Adote um runner padrão (pytest / Vitest / Jest) e exponha-o nos scripts de pacote.",
        ))

    # --- CI / Entrega ---
    if not stack.ci_tools:
        issues.append(_make_issue(
            "ci.missing",
            severity="high",
            category="Entrega",
            title="Sem configuração de CI",
            description="Nenhum workflow de CI foi detectado, o que torna regressões fáceis de entrar na main.",
            evidence=["Nenhuma config de GitHub Actions, GitLab CI, CircleCI, Jenkins ou Travis encontrada."],
            recommendation="Adicione um workflow de GitHub Actions (ou equivalente) rodando lint e testes a cada PR.",
        ))
    if not stack.containerization:
        issues.append(_make_issue(
            "delivery.no_docker",
            severity="medium",
            category="Entrega",
            title="Sem setup de container",
            description="Nenhum Dockerfile ou arquivo compose foi detectado. Novos colaboradores precisam montar a stack manualmente.",
            evidence=["Nenhum Dockerfile / docker-compose encontrado."],
            recommendation="Adicione um Dockerfile e um docker-compose.yml para um run local com um comando só.",
        ))

    # --- Lint / formatter ---
    has_lint = any("eslint" in c.lower() or "ruff" in c.lower() or "flake8" in c.lower() for c in scan.config_files)
    has_format = any("prettier" in c.lower() for c in scan.config_files) or any(
        "tool.black" in (scan.manifests.get(m, "")) for m in ("pyproject.toml",)
    )
    if not has_lint:
        issues.append(_make_issue(
            "quality.no_lint",
            severity="medium",
            category="Qualidade",
            title="Sem configuração de lint",
            description="Nenhuma configuração de ESLint / Ruff / Flake8 foi detectada.",
            evidence=["Nenhum .eslintrc*, ruff.toml, .flake8 ou equivalente encontrado."],
            recommendation="Adote um linter e rode-o no CI.",
        ))
    if not has_format:
        issues.append(_make_issue(
            "quality.no_formatter",
            severity="low",
            category="Qualidade",
            title="Sem configuração de formatter",
            description="Nenhuma configuração de Prettier ou Black foi detectada.",
            evidence=["Nenhuma config de prettier / black nem seção tool.black encontrada."],
            recommendation="Adote um formatter (Prettier / Black) e imponha-o no CI.",
        ))

    # --- Higiene de env ---
    env_names = [f.lower() for f in scan.env_files]
    real_env_committed = any(
        (n.endswith(".env") or n.endswith("/.env")) and "example" not in n and "sample" not in n and "template" not in n
        for n in env_names
    )
    example_env = any("example" in n or "sample" in n or "template" in n for n in env_names)
    if real_env_committed:
        issues.append(_make_issue(
            "security.env_committed",
            severity="critical",
            category="Segurança",
            title=".env aparenta estar commitado",
            description="Um .env real foi encontrado no repositório, o que frequentemente vaza segredos.",
            evidence=[f"Arquivos env encontrados: {', '.join(f for f in scan.env_files if 'example' not in f.lower())}"],
            recommendation="Remova o .env do versionamento, rotacione credenciais vazadas e adicione .env ao .gitignore.",
        ))
    if not example_env:
        issues.append(_make_issue(
            "config.no_env_example",
            severity="medium",
            category="Configuração",
            title="Sem .env.example commitado",
            description="Colaboradores não têm como saber quais variáveis de ambiente são esperadas.",
            evidence=["Nenhum .env.example / .env.sample / .env.template encontrado."],
            recommendation="Commite um .env.example com cada variável nomeada e documentada.",
        ))

    # --- Segredos / arquivos suspeitos ---
    if scan.suspicious_files:
        issues.append(_make_issue(
            "security.secret_like_files",
            severity="critical",
            category="Segurança",
            title="Arquivos potencialmente sensíveis commitados",
            description="Arquivos com nomes sugestivos de segredos foram detectados.",
            evidence=[f"Arquivos suspeitos: {', '.join(scan.suspicious_files[:10])}"],
            recommendation="Audite esses caminhos; se contiverem credenciais reais, rotacione-as e limpe do histórico do git.",
        ))

    # --- Higiene do repositório ---
    if not any(c.lower() == ".gitignore" for c in scan.config_files):
        issues.append(_make_issue(
            "hygiene.no_gitignore",
            severity="medium",
            category="Higiene",
            title="Sem .gitignore",
            description="Sem um .gitignore, é fácil commitar artefatos de build ou segredos por acidente.",
            evidence=["Nenhum .gitignore encontrado."],
            recommendation="Commite um .gitignore adequado à stack (Node / Python / Go / etc.).",
        ))

    top = {t.lower() for t in scan.top_level_dirs}
    if "node_modules" in top:
        issues.append(_make_issue(
            "hygiene.node_modules_committed",
            severity="high",
            category="Higiene",
            title="node_modules aparenta estar commitado",
            description="node_modules é uma pasta de dependências regenerável e nunca deve ser versionada.",
            evidence=["'node_modules' presente como diretório de topo."],
            recommendation="Remova node_modules do repositório e garanta que esteja no .gitignore.",
        ))
    if "dist" in top or "build" in top or "out" in top:
        issues.append(_make_issue(
            "hygiene.build_artifacts",
            severity="medium",
            category="Higiene",
            title="Saída de build commitada",
            description="Um diretório dist/, build/ ou out/ está sendo versionado.",
            evidence=[f"Pastas de topo incluem: {', '.join(sorted(top & {'dist', 'build', 'out'}))}"],
            recommendation="Saídas de build devem ser geradas no CI, não commitadas.",
        ))

    if len(scan.large_files) >= 5:
        issues.append(_make_issue(
            "hygiene.large_files",
            severity="medium",
            category="Higiene",
            title="Muitos arquivos grandes commitados",
            description=f"{len(scan.large_files)} arquivos passam de 1 MB e estão sendo versionados diretamente.",
            evidence=[f"Maior exemplo: {scan.large_files[0][0]} ({scan.large_files[0][1]} bytes)"],
            recommendation="Mova binários grandes para Git LFS ou storage externo.",
        ))

    # --- Cheiro de arquitetura ---
    if scan.max_depth > 12:
        issues.append(_make_issue(
            "architecture.deep_tree",
            severity="low",
            category="Arquitetura",
            title="Árvore de diretórios muito profunda",
            description="Aninhamento profundo dificulta navegação e refatoração.",
            evidence=[f"Profundidade máxima: {scan.max_depth}."],
            recommendation="Achate pastas onde possível; busque ≤ 8 níveis de aninhamento.",
        ))

    return issues
