"""Infer frameworks / stacks from manifest files and directory shape.

Everything here is deterministic and grounded in scanner output.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .scanner import ScanResult


@dataclass
class StackDetection:
    primary_languages: list[str] = field(default_factory=list)
    probable_frontend: list[str] = field(default_factory=list)
    probable_backend: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    databases: list[str] = field(default_factory=list)
    testing_tools: list[str] = field(default_factory=list)
    ci_tools: list[str] = field(default_factory=list)
    containerization: list[str] = field(default_factory=list)
    inferred_project_type: str = "Unknown"


FRONTEND_HINTS = {
    "react": "React",
    "next": "Next.js",
    "vue": "Vue.js",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "astro": "Astro",
    "vite": "Vite",
    "webpack": "Webpack",
    "tailwindcss": "Tailwind CSS",
    "redux": "Redux",
    "zustand": "Zustand",
    "@tanstack/react-query": "React Query",
}

BACKEND_HINTS = {
    "express": "Express",
    "fastify": "Fastify",
    "koa": "Koa",
    "nestjs": "NestJS",
    "@nestjs/core": "NestJS",
    "hapi": "Hapi",
}

TESTING_HINTS = {
    "jest": "Jest",
    "vitest": "Vitest",
    "mocha": "Mocha",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "@testing-library/react": "React Testing Library",
    "pytest": "pytest",
    "unittest": "unittest",
    "go test": "go test",
}

DATABASE_HINTS = {
    "prisma": "Prisma",
    "typeorm": "TypeORM",
    "mongoose": "MongoDB (mongoose)",
    "mongodb": "MongoDB",
    "sequelize": "Sequelize",
    "drizzle-orm": "Drizzle ORM",
    "pg": "PostgreSQL",
    "psycopg": "PostgreSQL",
    "psycopg2": "PostgreSQL",
    "psycopg2-binary": "PostgreSQL",
    "sqlalchemy": "SQLAlchemy",
    "redis": "Redis",
    "mysql2": "MySQL",
    "mysqlclient": "MySQL",
}

PY_BACKEND_HINTS = {
    "fastapi": "FastAPI",
    "uvicorn": "Uvicorn",
    "flask": "Flask",
    "django": "Django",
    "starlette": "Starlette",
    "pyramid": "Pyramid",
    "tornado": "Tornado",
    "celery": "Celery",
}

PY_TEST_HINTS = {"pytest", "unittest", "nose", "nose2"}


def _parse_package_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _deps_from_package_json(pkg: dict) -> list[str]:
    deps: list[str] = []
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section = pkg.get(key)
        if isinstance(section, dict):
            deps.extend(section.keys())
    return [d.lower() for d in deps]


def _parse_requirements_txt(text: str) -> list[str]:
    packages = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        # Split on specifiers: ==, >=, <=, ~=, !=, [extras]
        name = re.split(r"[=<>!~\[;]", line, maxsplit=1)[0].strip()
        if name:
            packages.append(name.lower())
    return packages


def _parse_pyproject(text: str) -> list[str]:
    # Very lightweight: extract names between quotes inside any dependencies block.
    packages: set[str] = set()
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"dependencies\s*=\s*\[", line):
            in_block = True
            # Same-line entries
            tail = line.split("[", 1)[1]
            for m in re.finditer(r'"([^"=<>!~\[;]+)', tail):
                packages.add(m.group(1).strip().lower())
            if "]" in tail:
                in_block = False
            continue
        if in_block:
            if "]" in line:
                in_block = False
            for m in re.finditer(r'"([^"=<>!~\[;]+)', line):
                packages.add(m.group(1).strip().lower())
    return list(packages)


def detect_stack(scan: ScanResult) -> StackDetection:
    det = StackDetection()

    # Primary languages: by code bytes, top 3
    ordered_langs = [
        lang
        for lang, _ in sorted(
            scan.language_bytes.items(), key=lambda x: x[1], reverse=True
        )
    ]
    code_langs = [
        lang for lang in ordered_langs
        if lang not in {"JSON", "YAML", "TOML", "INI", "XML", "Markdown", "reST", "Text", "CSV"}
    ]
    det.primary_languages = code_langs[:3]

    # Package managers from lockfiles / manifests
    mf = scan.manifests
    dep_files = {p.lower() for p in scan.dependency_files}
    if "package.json" in mf:
        if any("pnpm-lock.yaml" in d for d in dep_files):
            det.package_managers.append("pnpm")
        elif any("yarn.lock" in d for d in dep_files):
            det.package_managers.append("yarn")
        elif any("bun.lockb" in d for d in dep_files):
            det.package_managers.append("bun")
        else:
            det.package_managers.append("npm")
    if "requirements.txt" in mf or "pyproject.toml" in mf or "pipfile" in mf:
        if "poetry.lock" in mf or ("pyproject.toml" in mf and "poetry" in mf.get("pyproject.toml", "")):
            det.package_managers.append("poetry")
        else:
            det.package_managers.append("pip")
    if "cargo.toml" in mf:
        det.package_managers.append("cargo")
    if "go.mod" in mf:
        det.package_managers.append("go modules")
    if "gemfile" in mf:
        det.package_managers.append("bundler")

    # JS/TS dependencies
    js_deps: list[str] = []
    if "package.json" in mf:
        pkg = _parse_package_json(mf["package.json"])
        js_deps = _deps_from_package_json(pkg)
        # Package scripts can reveal tools too
        scripts = pkg.get("scripts") or {}
        script_blob = " ".join(
            v.lower() for v in scripts.values() if isinstance(v, str)
        )
        for hint, label in {
            **FRONTEND_HINTS,
            **BACKEND_HINTS,
            **TESTING_HINTS,
            **DATABASE_HINTS,
        }.items():
            if hint in script_blob and label not in det.frameworks + det.testing_tools + det.databases:
                pass  # fall through to dep-based detection below

    for dep in js_deps:
        if dep in FRONTEND_HINTS:
            det.probable_frontend.append(FRONTEND_HINTS[dep])
            if FRONTEND_HINTS[dep] not in det.frameworks and FRONTEND_HINTS[dep] in {
                "React", "Next.js", "Vue.js", "Nuxt", "Svelte", "SvelteKit", "Astro"
            }:
                det.frameworks.append(FRONTEND_HINTS[dep])
        if dep in BACKEND_HINTS:
            det.probable_backend.append(BACKEND_HINTS[dep])
            if BACKEND_HINTS[dep] not in det.frameworks:
                det.frameworks.append(BACKEND_HINTS[dep])
        if dep in TESTING_HINTS:
            if TESTING_HINTS[dep] not in det.testing_tools:
                det.testing_tools.append(TESTING_HINTS[dep])
        if dep in DATABASE_HINTS:
            if DATABASE_HINTS[dep] not in det.databases:
                det.databases.append(DATABASE_HINTS[dep])

    # Python dependencies
    py_deps: set[str] = set()
    if "requirements.txt" in mf:
        py_deps.update(_parse_requirements_txt(mf["requirements.txt"]))
    if "pyproject.toml" in mf:
        py_deps.update(_parse_pyproject(mf["pyproject.toml"]))
    for dep in py_deps:
        if dep in PY_BACKEND_HINTS:
            det.probable_backend.append(PY_BACKEND_HINTS[dep])
            if PY_BACKEND_HINTS[dep] not in det.frameworks:
                det.frameworks.append(PY_BACKEND_HINTS[dep])
        if dep in PY_TEST_HINTS and dep not in det.testing_tools:
            det.testing_tools.append(dep)
        if dep in DATABASE_HINTS:
            if DATABASE_HINTS[dep] not in det.databases:
                det.databases.append(DATABASE_HINTS[dep])

    # Infra / CI / containers
    if scan.container_files:
        det.containerization.append("Docker")
        if any(f.lower().startswith(("docker-compose", "compose")) for f in scan.container_files):
            det.containerization.append("docker-compose")

    for f in scan.ci_files:
        low = f.lower()
        if low.startswith(".github/workflows/"):
            if "GitHub Actions" not in det.ci_tools:
                det.ci_tools.append("GitHub Actions")
        elif low == ".gitlab-ci.yml":
            det.ci_tools.append("GitLab CI")
        elif low == ".circleci/config.yml":
            det.ci_tools.append("CircleCI")
        elif low == ".travis.yml":
            det.ci_tools.append("Travis CI")
        elif low == "jenkinsfile":
            det.ci_tools.append("Jenkins")
        elif low == "azure-pipelines.yml":
            det.ci_tools.append("Azure Pipelines")

    # Directory-shape fallbacks
    top = {t.lower() for t in scan.top_level_dirs}
    if "frontend" in top or "web" in top or "client" in top:
        if not det.probable_frontend:
            det.probable_frontend.append("Pasta frontend customizada")
    if "backend" in top or "api" in top or "server" in top:
        if not det.probable_backend:
            det.probable_backend.append("Pasta backend customizada")

    # Inferência do tipo de projeto
    has_frontend = bool(det.probable_frontend)
    has_backend = bool(det.probable_backend)
    if has_frontend and has_backend:
        det.inferred_project_type = "Aplicação full-stack"
    elif has_frontend:
        det.inferred_project_type = "Aplicação frontend"
    elif has_backend:
        det.inferred_project_type = "Serviço backend"
    elif "go.mod" in mf or "cargo.toml" in mf:
        det.inferred_project_type = "Serviço backend"
    elif "package.json" in mf and "react" in js_deps:
        det.inferred_project_type = "Aplicação frontend"
    elif "python" in (det.primary_languages[:1] or [""])[0].lower() if det.primary_languages else False:
        det.inferred_project_type = "Projeto Python"
    else:
        if det.primary_languages:
            det.inferred_project_type = f"Projeto {det.primary_languages[0]}"
        else:
            det.inferred_project_type = "Repositório de uso geral"

    # Deduplicate while preserving order
    def _dedupe(xs: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    det.probable_frontend = _dedupe(det.probable_frontend)
    det.probable_backend = _dedupe(det.probable_backend)
    det.frameworks = _dedupe(det.frameworks)
    det.testing_tools = _dedupe(det.testing_tools)
    det.databases = _dedupe(det.databases)
    det.ci_tools = _dedupe(det.ci_tools)
    det.containerization = _dedupe(det.containerization)
    det.package_managers = _dedupe(det.package_managers)
    return det
