from pathlib import Path

EXT_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".c": "c",
    ".h": "c-header",
    ".cpp": "cpp",
    ".hpp": "cpp-header",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".swift": "swift",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".md": "markdown",
    ".sql": "sql",
    ".sh": "shell",
    ".ps1": "powershell",
    ".bat": "batch",
    ".dockerfile": "dockerfile",
}

TEXT_EXTENSIONS = set(EXT_TO_LANGUAGE.keys()) | {
    ".txt",
    ".csv",
    ".xml",
    ".svg",
    ".conf",
    ".cfg",
    ".env.example",
}


def detect_language(path: Path) -> str:
    name = path.name.lower()
    if name == "dockerfile":
        return "dockerfile"
    return EXT_TO_LANGUAGE.get(path.suffix.lower(), "text")


def looks_textual(path: Path) -> bool:
    name = path.name.lower()
    if name == "dockerfile":
        return True
    if name.endswith(".env.example"):
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS
