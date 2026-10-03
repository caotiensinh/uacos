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


def _package_name(rel_path: str) -> str:
    module = _module_name(rel_path)
    if rel_path.replace("\\", "/").endswith("/__init__.py") or rel_path == "__init__.py":
        return module
    return module.rsplit(".", 1)[0] if "." in module else ""


def _canonical_symbol_id(module: str, qname: str) -> str:
    return f"{module}:{qname}" if module else qname


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


def _resolve_import_module(record: dict, rel_path: str) -> str:
    module = str(record.get("module") or "")
    level = int(record.get("level") or 0)
    if level <= 0:
        return module

    package = _package_name(rel_path)
    parts = [p for p in package.split(".") if p]
    up = max(0, level - 1)
    if up:
        parts = parts[: max(0, len(parts) - up)]
    if module:
        parts.extend([p for p in module.split(".") if p])
    return ".".join(parts)


def _symbol_records(parsed: list[dict]) -> tuple[list[dict], dict[str, list[str]]]:
    symbols = []
    aliases: dict[str, list[str]] = {}

    for doc in parsed:
        module = _module_name(doc["path"])
        groups = [
            ("function", doc.get("functions", [])),
            ("async_function", doc.get("async_functions", [])),
            ("method", doc.get("methods", [])),
            ("class", doc.get("classes", [])),
        ]
        for kind, items in groups:
            for item in items:
                qname = item.get("qname") or item.get("name")
                if not qname:
                    continue
                symbol_id = _canonical_symbol_id(module, qname)
                record = {
                    "id": symbol_id,
                    "name": item.get("name") or qname.split(".")[-1],
                    "qname": qname,
                    "module": module,
                    "file": doc["path"],
                    "kind": kind,
                    "lineno": item.get("lineno"),
                    "end_lineno": item.get("end_lineno"),
                    "language": doc.get("language", "python"),
                }
                if kind == "class":
                    record["bases"] = item.get("bases", [])
                symbols.append(record)

                for alias in {
                    symbol_id,
                    record["name"],
                    qname,
                    f"{module}.{qname}" if module else qname,
                }:
                    aliases.setdefault(alias, []).append(symbol_id)

    for key in list(aliases):
        aliases[key] = sorted(set(aliases[key]))
    return symbols, aliases


def _resolve_symbol(alias_map: dict[str, list[str]], module: str, name: str) -> tuple[str | None, str, int]:
    candidates = []
    for alias in (
        _canonical_symbol_id(module, name),
        f"{module}.{name}" if module else name,
        name,
        name.split(".")[-1],
    ):
        candidates.extend(alias_map.get(alias, []))
    unique = sorted(set(candidates))
    if len(unique) == 1:
        return unique[0], "exact_or_unambiguous_alias", 1
    if len(unique) > 1:
        return None, "ambiguous", len(unique)
    return None, "unresolved", 0


def build_graph(repo_root: Path, include_tests: bool = True) -> dict:
    parsed = parse_repo_python(repo_root, include_tests=include_tests)
    module_to_file = {_module_name(d["path"]): d["path"] for d in parsed}
    symbols, symbol_aliases = _symbol_records(parsed)
    symbol_by_id = {row["id"]: row for row in symbols}

    # Backward-compatible map. Canonical IDs are authoritative; ambiguous short
    # aliases keep their first deterministic match instead of silently changing.
    symbol_to_file = {}
    file_symbols = {}
    for row in symbols:
        symbol_to_file[row["id"]] = row["file"]
        symbol_to_file.setdefault(row["qname"], row["file"])
        symbol_to_file.setdefault(row["name"], row["file"])
        file_symbols.setdefault(row["file"], []).append(row["id"])
    for path in list(file_symbols):
        file_symbols[path] = sorted(set(file_symbols[path]))

    file_edges = []
    seen_file_edges = set()
    for d in parsed:
        src = d["path"]
        records = d.get("import_records") or []
        if records:
            for record in records:
                base_module = _resolve_import_module(record, src)
                import_name = base_module
                if record.get("kind") == "from" and record.get("name") and record.get("name") != "*":
                    import_name = f"{base_module}.{record['name']}" if base_module else str(record["name"])
                dst = _import_to_file(import_name, module_to_file) or _import_to_file(base_module, module_to_file)
                if dst and dst != src:
                    key = (src, dst, import_name)
                    if key not in seen_file_edges:
                        seen_file_edges.add(key)
                        file_edges.append({
                            "source": src,
                            "target": dst,
                            "kind": "import",
                            "import": import_name,
                            "level": record.get("level", 0),
                        })
        else:
            for imp in d.get("imports", []):
                dst = _import_to_file(imp, module_to_file)
                if dst and dst != src:
                    key = (src, dst, imp)
                    if key not in seen_file_edges:
                        seen_file_edges.add(key)
                        file_edges.append({"source": src, "target": dst, "kind": "import", "import": imp})

    call_edges = []
    for d in parsed:
        src_file = d["path"]
        module = _module_name(src_file)
        for call in d.get("calls", []):
            callee = call.get("callee", "")
            target_symbol_id, resolution, candidate_count = _resolve_symbol(symbol_aliases, module, callee)
            target_file = symbol_by_id.get(target_symbol_id, {}).get("file") if target_symbol_id else None
            caller = call.get("caller")
            source_symbol_id = None
            if caller and caller != "<module>":
                source_symbol_id, _, _ = _resolve_symbol(symbol_aliases, module, caller)
            call_edges.append({
                "source_file": src_file,
                "source_symbol_id": source_symbol_id,
                "caller": caller,
                "callee": callee,
                "target_symbol_id": target_symbol_id,
                "target_file": target_file,
                "resolution": resolution,
                "candidate_count": candidate_count,
                "lineno": call.get("lineno"),
            })

    graph = {
        "version": 2,
        "created_at": utcnow(),
        "repo": str(repo_root),
        "files": [d["path"] for d in parsed],
        "parsed": parsed,
        "module_to_file": module_to_file,
        "symbols": symbols,
        "symbol_aliases": symbol_aliases,
        "symbol_to_file": symbol_to_file,
        "file_symbols": file_symbols,
        "file_edges": file_edges,
        "call_edges": call_edges,
        "stats": {
            "file_count": len(parsed),
            "file_edge_count": len(file_edges),
            "call_edge_count": len(call_edges),
            "resolved_call_edge_count": len([e for e in call_edges if e.get("target_symbol_id")]),
            "ambiguous_call_edge_count": len([e for e in call_edges if e.get("resolution") == "ambiguous"]),
            "symbol_count": len(symbols),
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
