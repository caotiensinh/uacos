from dataclasses import dataclass
import re

@dataclass
class Symbol:
    name: str
    kind: str
    start_line: int
    end_line: int
    signature: str

PY_PATTERNS = [
    ("class", re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b")),
    ("function", re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")),
]

JS_PATTERNS = [
    ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_$][A-Za-z0-9_$]*)")),
    ("function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")),
    ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")),
]

GO_PATTERNS = [
    ("function", re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(")),
    ("struct", re.compile(r"^\s*type\s+([A-Za-z_][A-Za-z0-9_]*)\s+struct\s*\{")),
    ("interface", re.compile(r"^\s*type\s+([A-Za-z_][A-Za-z0-9_]*)\s+interface\s*\{")),
]

RUST_PATTERNS = [
    ("function", re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")),
    ("struct", re.compile(r"^\s*(?:pub\s+)?struct\s+([A-Za-z_][A-Za-z0-9_]*)")),
    ("enum", re.compile(r"^\s*(?:pub\s+)?enum\s+([A-Za-z_][A-Za-z0-9_]*)")),
]

COMMON_PATTERNS = [
    ("class", re.compile(r"^\s*(?:public|private|protected|final|abstract|static|\s)*class\s+([A-Za-z_][A-Za-z0-9_]*)")),
    ("interface", re.compile(r"^\s*(?:public|private|protected|\s)*interface\s+([A-Za-z_][A-Za-z0-9_]*)")),
    ("function", re.compile(r"^\s*(?:public|private|protected|static|final|virtual|inline|constexpr|\s)+[A-Za-z_][A-Za-z0-9_<>,:\*\&\s]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*(?:\{|$)")),
]

HTML_PATTERNS = [
    ("id", re.compile("id=[\\\"']([A-Za-z_][A-Za-z0-9_\\-:]*)[\\\"']")),
    ("class_attr", re.compile("class=[\\\"']([^\\\"']+)[\\\"']")),
]

CSS_PATTERNS = [
    ("css_class", re.compile(r"^\s*\.([A-Za-z_][A-Za-z0-9_-]*)\s*[\{,]")),
    ("css_id", re.compile(r"^\s*#([A-Za-z_][A-Za-z0-9_-]*)\s*[\{,]")),
]

SHELL_PATTERNS = [
    ("function", re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{")),
    ("function", re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{")),
]

def _patterns(language):
    if language == "python":
        return PY_PATTERNS
    if language in {"javascript", "javascript-react", "typescript", "typescript-react"}:
        return JS_PATTERNS
    if language == "go":
        return GO_PATTERNS
    if language == "rust":
        return RUST_PATTERNS
    if language in {"java", "kotlin", "c", "c-header", "cpp", "cpp-header", "csharp", "php"}:
        return COMMON_PATTERNS
    if language == "html":
        return HTML_PATTERNS
    if language in {"css", "scss"}:
        return CSS_PATTERNS
    if language in {"shell", "powershell", "batch"}:
        return SHELL_PATTERNS
    return []

def _end_line(lines, start_idx, language):
    if language == "python":
        start = lines[start_idx]
        indent = len(start) - len(start.lstrip(" "))
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            current = len(line) - len(line.lstrip(" "))
            if current <= indent and not line.lstrip().startswith(("#", "@")):
                return i
        return len(lines)

    braces = 0
    seen = False
    for i in range(start_idx, min(len(lines), start_idx + 200)):
        braces += lines[i].count("{")
        braces -= lines[i].count("}")
        if "{" in lines[i]:
            seen = True
        if seen and braces <= 0:
            return i + 1
    return min(len(lines), start_idx + 1)

def extract_symbols(text, language):
    lines = text.splitlines()
    out = []
    seen = set()
    for idx, line in enumerate(lines):
        for kind, pattern in _patterns(language):
            for m in pattern.finditer(line):
                raw = m.group(1)
                names = raw.split() if kind == "class_attr" else [raw]
                for name in names:
                    key = (name, kind, idx + 1)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(Symbol(name, kind, idx + 1, _end_line(lines, idx, language), line.strip()[:240]))
    return out
