"""Language classification by file extension / filename."""

from __future__ import annotations

from dataclasses import dataclass

# Extension → (language name, is_code)
EXT_TO_LANGUAGE: dict[str, tuple[str, bool]] = {
    # JS/TS ecosystem
    ".js": ("JavaScript", True),
    ".jsx": ("JavaScript", True),
    ".mjs": ("JavaScript", True),
    ".cjs": ("JavaScript", True),
    ".ts": ("TypeScript", True),
    ".tsx": ("TypeScript", True),
    # Python
    ".py": ("Python", True),
    ".pyi": ("Python", True),
    # Web
    ".html": ("HTML", True),
    ".htm": ("HTML", True),
    ".css": ("CSS", True),
    ".scss": ("SCSS", True),
    ".sass": ("SCSS", True),
    ".less": ("CSS", True),
    ".vue": ("Vue", True),
    ".svelte": ("Svelte", True),
    ".astro": ("Astro", True),
    # JVM / systems
    ".java": ("Java", True),
    ".kt": ("Kotlin", True),
    ".kts": ("Kotlin", True),
    ".scala": ("Scala", True),
    ".go": ("Go", True),
    ".rs": ("Rust", True),
    ".c": ("C", True),
    ".h": ("C", True),
    ".cpp": ("C++", True),
    ".hpp": ("C++", True),
    ".cs": ("C#", True),
    ".fs": ("F#", True),
    ".swift": ("Swift", True),
    ".m": ("Objective-C", True),
    ".mm": ("Objective-C", True),
    # Scripting
    ".rb": ("Ruby", True),
    ".php": ("PHP", True),
    ".pl": ("Perl", True),
    ".sh": ("Shell", True),
    ".bash": ("Shell", True),
    ".zsh": ("Shell", True),
    ".ps1": ("PowerShell", True),
    ".lua": ("Lua", True),
    ".r": ("R", True),
    ".jl": ("Julia", True),
    ".dart": ("Dart", True),
    ".ex": ("Elixir", True),
    ".exs": ("Elixir", True),
    ".erl": ("Erlang", True),
    ".clj": ("Clojure", True),
    ".hs": ("Haskell", True),
    # Data / config (not counted as code)
    ".json": ("JSON", False),
    ".yaml": ("YAML", False),
    ".yml": ("YAML", False),
    ".toml": ("TOML", False),
    ".ini": ("INI", False),
    ".xml": ("XML", False),
    ".md": ("Markdown", False),
    ".mdx": ("Markdown", False),
    ".rst": ("reST", False),
    ".txt": ("Text", False),
    ".csv": ("CSV", False),
    ".tsv": ("CSV", False),
    # Queries
    ".sql": ("SQL", True),
    ".graphql": ("GraphQL", True),
    ".gql": ("GraphQL", True),
    # Build / infra
    ".dockerfile": ("Dockerfile", False),
    ".tf": ("Terraform", True),
    ".hcl": ("HCL", True),
    ".proto": ("Protobuf", True),
    ".cmake": ("CMake", True),
    ".mk": ("Makefile", True),
}

FILENAME_TO_LANGUAGE: dict[str, str] = {
    "dockerfile": "Dockerfile",
    "makefile": "Makefile",
    "rakefile": "Ruby",
    "gemfile": "Ruby",
    "gemfile.lock": "Ruby",
    "pipfile": "Python",
    "cargo.toml": "Rust",
    "cargo.lock": "Rust",
    "go.mod": "Go",
    "go.sum": "Go",
    "package.json": "JavaScript",
    "pnpm-lock.yaml": "JavaScript",
    "yarn.lock": "JavaScript",
    "bun.lockb": "JavaScript",
    "tsconfig.json": "TypeScript",
}

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp", ".tiff",
    ".pdf", ".zip", ".tar", ".gz", ".tgz", ".bz2", ".rar", ".7z",
    ".mp3", ".mp4", ".mov", ".avi", ".webm", ".wav", ".flac",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".exe", ".dll", ".so", ".dylib", ".a", ".o", ".class", ".jar",
    ".pyc", ".pyo", ".whl", ".DS_Store",
}


@dataclass
class FileClassification:
    language: str | None
    is_code: bool
    is_binary: bool


def classify(filename: str) -> FileClassification:
    name = filename.lower()
    # Filename-first match
    if name in FILENAME_TO_LANGUAGE:
        return FileClassification(FILENAME_TO_LANGUAGE[name], True, False)

    dot = name.rfind(".")
    if dot == -1:
        # Files without extension: Dockerfile, Makefile, etc.
        return FileClassification(None, False, False)
    ext = name[dot:]
    if ext in BINARY_EXTS:
        return FileClassification(None, False, True)
    if ext in EXT_TO_LANGUAGE:
        lang, is_code = EXT_TO_LANGUAGE[ext]
        return FileClassification(lang, is_code, False)
    return FileClassification(None, False, False)
