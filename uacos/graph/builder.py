from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone
from uacos.config import uacos_dir
from uacos.ast_engine.parser import parse_repo_python

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def graph_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "graph"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _module_name(rel_path: str) -> str:
    rel = rel_path[:-3] if rel_path.endswith(".py") else rel_path
    parts = [p for p in rel.replace("\\", "/").split("/") if p != "__init__"]
    return ".".join(parts)

def _import_to_file(import_name: str, module_to_file: dict[str, str]) -> str | None:
    if import_name in module_to_file:
        return module_to_file[import_name]
    parts = import_name.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in module_to_file:
            return module_to_file[candidate]
        parts.pop()
    return None

def build_graph(repo_root: Path, include_tests: bool = True) -> dict:
    parsed = parse_repo_python(repo_root, include_tests=include_tests)
    module_to_file = {_module_name(d["path"]): d["path"] for d in parsed}
    symbol_to_file = {}
    file_symbols = {}

    for d in parsed:
        syms = []
        for kind in ["functions", "async_functions", "methods"]:
            for item in d.get(kind, []):
                symbol_to_file[item["qname"]] = d["path"]
                symbol_to_file[item["name"]] = d["path"]
                syms.append(item["qname"])
        for item in d.get("classes", []):
            symbol_to_file[item["name"]] = d["path"]
            syms.append(item["name"])
        file_symbols[d["path"]] = sorted(set(syms))

    file_edges = []
    for d in parsed:
        src = d["path"]
        for imp in d.get("imports", []):
            dst = _import_to_file(imp, module_to_file)
            if dst and dst != src:
                file_edges.append({"source": src, "target": dst, "kind": "import", "import": imp})

    call_edges = []
    for d in parsed:
        src_file = d["path"]
        for call in d.get("calls", []):
            callee = call.get("callee", "")
            target_file = symbol_to_file.get(callee) or symbol_to_file.get(callee.split(".")[-1])
            call_edges.append({
                "source_file": src_file,
                "caller": call.get("caller"),
                "callee": callee,
                "target_file": target_file,
                "lineno": call.get("lineno"),
            })

    graph = {
        "version": 1,
        "created_at": utcnow(),
        "repo": str(repo_root),
        "files": [d["path"] for d in parsed],
        "parsed": parsed,
        "module_to_file": module_to_file,
        "symbol_to_file": symbol_to_file,
        "file_symbols": file_symbols,
        "file_edges": file_edges,
        "call_edges": call_edges,
        "stats": {
            "file_count": len(parsed),
            "file_edge_count": len(file_edges),
            "call_edge_count": len(call_edges),
            "symbol_count": len(symbol_to_file),
            "parse_errors": len([d for d in parsed if d.get("parse_error")]),
        },
    }
    gd = graph_dir(repo_root)
    (gd / "ast_index.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (gd / "dependency_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "graph_dir": str(gd), "stats": graph["stats"]}

def load_graph(repo_root: Path, auto_build: bool = True) -> dict:
    path = graph_dir(repo_root) / "dependency_graph.json"
    if not path.exists():
        if not auto_build:
            raise FileNotFoundError(str(path))
        build_graph(repo_root)
    return json.loads(path.read_text(encoding="utf-8"))
