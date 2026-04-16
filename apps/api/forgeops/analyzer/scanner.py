"""Walk a repository directory and collect deterministic facts.

Output is a rich, typed dict-like structure consumed by the framework
detector, the scorer, the issue generator, and the markdown generator.
"""

from __future__ import annotations

import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .languages import classify

IGNORED_DIRNAMES = {
    ".git", ".hg", ".svn",
    "node_modules", ".pnpm-store", "bower_components",
    ".venv", "venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".next", ".nuxt", ".turbo", ".parcel-cache", ".cache",
    "dist", "build", "out", "target", "coverage",
    ".idea", ".vscode", ".DS_Store",
}

LARGE_FILE_THRESHOLD = 1 * 1024 * 1024  # 1 MB

TEST_DIR_HINTS = {"tests", "test", "__tests__", "spec", "specs", "e2e", "cypress", "playwright"}
DOCS_DIR_HINTS = {"docs", "documentation", "doc"}

CI_FILES = {
    ".github/workflows",
    ".gitlab-ci.yml",
    ".circleci/config.yml",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
    "jenkinsfile",
    ".drone.yml",
    ".travis.yml",
    "buildkite.yml",
    ".buildkite",
}

CONTAINER_FILES = {
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yaml",
    "compose.yml",
    ".dockerignore",
    "containerfile",
}

ENV_FILES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.example",
    ".env.sample",
    ".env.template",
}

DEPENDENCY_FILES = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb",
    "requirements.txt", "pyproject.toml", "poetry.lock", "pipfile", "pipfile.lock",
    "gemfile", "gemfile.lock",
    "cargo.toml", "cargo.lock",
    "go.mod", "go.sum",
    "composer.json", "composer.lock",
    "build.gradle", "build.gradle.kts", "pom.xml",
    "mix.exs", "mix.lock",
}

CONFIG_FILES = {
    ".editorconfig", ".eslintrc", ".eslintrc.json", ".eslintrc.js", ".eslintrc.cjs",
    ".prettierrc", ".prettierrc.json", ".prettierrc.js",
    "tsconfig.json", "tsconfig.base.json",
    "vite.config.ts", "vite.config.js", "webpack.config.js",
    "rollup.config.js", "babel.config.js", ".babelrc",
    "postcss.config.js", "tailwind.config.ts", "tailwind.config.js",
    "next.config.js", "next.config.mjs", "next.config.ts",
    "nuxt.config.ts", "svelte.config.js", "astro.config.mjs",
    "pyproject.toml", "setup.cfg", "setup.py", "tox.ini", "mypy.ini", "ruff.toml",
    ".flake8", ".pre-commit-config.yaml",
    "jest.config.js", "jest.config.ts", "vitest.config.ts", "playwright.config.ts",
    "cypress.config.ts", "cypress.config.js",
    ".gitignore", ".gitattributes",
}

LICENSE_FILES = {"license", "license.md", "license.txt", "licence", "licence.md"}
README_FILES = {"readme.md", "readme", "readme.rst", "readme.txt"}
CHANGELOG_FILES = {"changelog.md", "changelog", "changes.md", "history.md"}
CONTRIBUTING_FILES = {"contributing.md", "contributing"}
CODEOWNERS_FILES = {"codeowners"}

SUSPICIOUS_PATTERNS = [
    re.compile(r"\.(pem|key|crt|cer|p12|pfx)$"),
    re.compile(r"id_rsa"),
    re.compile(r"id_dsa"),
    re.compile(r"^secrets?\.(json|yaml|yml|env)$"),
    re.compile(r"credentials?\.(json|yaml|yml)$"),
    re.compile(r"\.aws/credentials$"),
    re.compile(r"token\.txt$"),
]


@dataclass
class ScanResult:
    total_files: int = 0
    total_directories: int = 0
    total_size_bytes: int = 0
    code_files: int = 0
    code_size_bytes: int = 0
    binary_files: int = 0
    file_depths: list[int] = field(default_factory=list)
    max_depth: int = 0

    language_files: Counter[str] = field(default_factory=Counter)
    language_bytes: Counter[str] = field(default_factory=Counter)
    extension_files: Counter[str] = field(default_factory=Counter)
    extension_bytes: Counter[str] = field(default_factory=Counter)

    file_paths: list[tuple[str, int]] = field(default_factory=list)

    # Categorized lists (relative paths)
    config_files: list[str] = field(default_factory=list)
    docs_files: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    ci_files: list[str] = field(default_factory=list)
    container_files: list[str] = field(default_factory=list)
    env_files: list[str] = field(default_factory=list)
    dependency_files: list[str] = field(default_factory=list)
    license_files: list[str] = field(default_factory=list)
    readme_files: list[str] = field(default_factory=list)
    changelog_files: list[str] = field(default_factory=list)
    contributing_files: list[str] = field(default_factory=list)
    codeowners_files: list[str] = field(default_factory=list)
    suspicious_files: list[str] = field(default_factory=list)
    large_files: list[tuple[str, int]] = field(default_factory=list)

    # Directory-level facts
    top_level_dirs: list[str] = field(default_factory=list)
    directory_depths: Counter[int] = field(default_factory=Counter)

    # Raw manifest contents the framework detector can consume
    manifests: dict[str, str] = field(default_factory=dict)

    # Remembered root path
    root_path: str = ""


def _posix(path: str) -> str:
    return path.replace("\\", "/")


def _rel(path: Path, root: Path) -> str:
    try:
        return _posix(str(path.relative_to(root)))
    except ValueError:
        return _posix(str(path))


def _should_ignore_dir(name: str) -> bool:
    return name in IGNORED_DIRNAMES or name.startswith(".")


def _is_suspicious(name: str) -> bool:
    # Note: `.env` is tracked separately under `env_files` and flagged by
    # `security.env_committed`; we deliberately do not double-count here.
    lower = name.lower()
    for pat in SUSPICIOUS_PATTERNS:
        if pat.search(lower):
            return True
    return False


def scan_repository(root: str | os.PathLike[str]) -> ScanResult:
    root_path = Path(root).resolve()
    result = ScanResult(root_path=str(root_path))

    if not root_path.exists() or not root_path.is_dir():
        return result

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune ignored directories but keep .github (for workflows)
        pruned = []
        for d in list(dirnames):
            if d == ".github":
                pruned.append(d)
                continue
            if _should_ignore_dir(d):
                continue
            pruned.append(d)
        dirnames[:] = pruned

        dir_path = Path(dirpath)
        rel_dir = _rel(dir_path, root_path)
        depth = 0 if rel_dir in ("", ".") else rel_dir.count("/") + 1
        result.directory_depths[depth] += 1
        if depth == 1:
            result.top_level_dirs.append(rel_dir)

        result.total_directories += 1

        for fname in filenames:
            result.total_files += 1
            fpath = dir_path / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                size = 0
            result.total_size_bytes += size

            rel_path = _rel(fpath, root_path)
            result.file_paths.append((rel_path, size))
            result.file_depths.append(depth + 1)
            if depth + 1 > result.max_depth:
                result.max_depth = depth + 1

            # Extension stats
            ext = fpath.suffix.lower() or "(no-ext)"
            result.extension_files[ext] += 1
            result.extension_bytes[ext] += size

            # Classification
            cls = classify(fname)
            if cls.language:
                result.language_files[cls.language] += 1
                result.language_bytes[cls.language] += size
            if cls.is_code:
                result.code_files += 1
                result.code_size_bytes += size
            if cls.is_binary:
                result.binary_files += 1

            # Categorization by relative path
            rel_lower = rel_path.lower()
            base_lower = fname.lower()

            # Test files
            parts_lower = [p.lower() for p in rel_path.split("/")]
            if any(p in TEST_DIR_HINTS for p in parts_lower):
                result.test_files.append(rel_path)
            elif cls.is_code and (
                base_lower.endswith((".test.ts", ".test.tsx", ".test.js", ".test.jsx"))
                or base_lower.endswith((".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx"))
                or base_lower.startswith("test_")
                or base_lower.endswith("_test.py")
                or base_lower.endswith("_test.go")
            ):
                result.test_files.append(rel_path)

            # Docs files
            if any(p in DOCS_DIR_HINTS for p in parts_lower) and base_lower.endswith((".md", ".mdx", ".rst")):
                result.docs_files.append(rel_path)
            elif base_lower.endswith((".md", ".mdx", ".rst")) and depth == 0:
                result.docs_files.append(rel_path)

            # CI files: github workflows + single-file CI configs
            if rel_lower.startswith(".github/workflows/") or base_lower in {
                ".gitlab-ci.yml",
                "azure-pipelines.yml",
                "bitbucket-pipelines.yml",
                "jenkinsfile",
                ".drone.yml",
                ".travis.yml",
                "buildkite.yml",
            } or rel_lower == ".circleci/config.yml":
                result.ci_files.append(rel_path)

            # Container files
            if base_lower in CONTAINER_FILES or base_lower.startswith("dockerfile"):
                result.container_files.append(rel_path)

            # Env files
            if base_lower in ENV_FILES:
                result.env_files.append(rel_path)

            # Dependency manifests
            if base_lower in DEPENDENCY_FILES:
                result.dependency_files.append(rel_path)
                # Record content of small manifests for framework detection
                if size < 200 * 1024:
                    try:
                        result.manifests[base_lower] = fpath.read_text(
                            encoding="utf-8", errors="ignore"
                        )
                    except OSError:
                        pass

            # Config files
            if base_lower in CONFIG_FILES or base_lower.startswith(("tsconfig.", "jest.config.", "vite.config.")):
                result.config_files.append(rel_path)

            # Markers
            if base_lower in LICENSE_FILES:
                result.license_files.append(rel_path)
            if base_lower in README_FILES and depth == 0:
                result.readme_files.append(rel_path)
                if size < 200 * 1024:
                    try:
                        result.manifests[base_lower] = fpath.read_text(
                            encoding="utf-8", errors="ignore"
                        )
                    except OSError:
                        pass
            if base_lower in CHANGELOG_FILES:
                result.changelog_files.append(rel_path)
            if base_lower in CONTRIBUTING_FILES:
                result.contributing_files.append(rel_path)
            if base_lower in CODEOWNERS_FILES:
                result.codeowners_files.append(rel_path)

            # Suspicious / secrets
            if _is_suspicious(base_lower):
                result.suspicious_files.append(rel_path)

            # Large files
            if size >= LARGE_FILE_THRESHOLD:
                result.large_files.append((rel_path, size))

    return result


def summarize_file_types(
    extension_files: Counter[str], extension_bytes: Counter[str], top: int = 10
) -> list[dict]:
    rows = []
    for ext, files in extension_files.most_common(top):
        rows.append(
            {
                "extension": ext,
                "files": files,
                "bytes": int(extension_bytes.get(ext, 0)),
            }
        )
    return rows


def summarize_languages(
    language_files: Counter[str], language_bytes: Counter[str]
) -> list[dict]:
    total = max(sum(language_bytes.values()), 1)
    langs = []
    for lang, bts in language_bytes.most_common():
        langs.append(
            {
                "language": lang,
                "files": int(language_files.get(lang, 0)),
                "bytes": int(bts),
                "share": round(bts / total, 4),
            }
        )
    return langs


def largest_files(files: Iterable[tuple[str, int]], top: int = 10) -> list[dict]:
    ordered = sorted(files, key=lambda x: x[1], reverse=True)[:top]
    return [{"path": p, "bytes": int(s)} for p, s in ordered]
