from __future__ import annotations

from collections.abc import Callable
import re


ImportResolver = Callable[[dict, dict], str]


def _normalize_type_name(value: str) -> str:
    value = str(value or "").strip()
    value = re.sub(r"<[^<>]*>", "", value)
    value = re.sub(r"\[[^\[\]]*\]", "", value)
    value = re.sub(r"\b(public|protected|private|virtual|extends|implements|class|struct)\b", " ", value)
    value = value.replace("::", ".").replace("$", ".")
    return re.sub(r"\s+", "", value).strip(".")


def _module_file_candidates(import_name: str, module_to_file: dict[str, str]) -> list[str]:
    import_name = str(import_name or "").strip(".")
    if not import_name:
        return []
    exact = module_to_file.get(import_name)
    if exact:
        return [exact]
    return sorted({
        path
        for module, path in module_to_file.items()
        if module.endswith(f".{import_name}") or import_name.endswith(f".{module}")
    })


def _imported_class_candidates(
    doc: dict,
    base_name: str,
    classes: list[dict],
    module_to_file: dict[str, str],
    resolve_import_module: ImportResolver,
) -> list[str]:
    terminal = base_name.rsplit(".", 1)[-1]
    candidates: set[str] = set()
    for record in doc.get("import_records") or []:
        language = str(doc.get("language") or "")
        record_module = _normalize_type_name(record.get("module") or "")
        record_name = _normalize_type_name(record.get("name") or "")
        alias = _normalize_type_name(record.get("alias") or "")

        local_names = {name for name in {alias, record_name, record_module.rsplit(".", 1)[-1]} if name}
        if language in {"c", "cpp"}:
            matches_local = True
        else:
            matches_local = terminal in local_names or base_name in {record_module, record_name}
        if not matches_local:
            continue

        resolved_module = _normalize_type_name(resolve_import_module(record, doc))
        file_candidates = _module_file_candidates(resolved_module, module_to_file)
        if language == "python" and record.get("kind") == "from" and record_name:
            file_candidates.extend(_module_file_candidates(resolved_module, module_to_file))
        if language == "java" and record_module:
            file_candidates.extend(_module_file_candidates(record_module, module_to_file))

        target_name = record_name or record_module.rsplit(".", 1)[-1] or terminal
        for row in classes:
            if row["file"] in file_candidates and row["name"] in {terminal, target_name}:
                candidates.add(row["id"])
    return sorted(candidates)


def _global_class_candidates(base_name: str, source_module: str, aliases: dict[str, list[str]]) -> list[str]:
    terminal = base_name.rsplit(".", 1)[-1]
    candidates: set[str] = set()
    for alias in (
        f"{source_module}:{base_name}" if source_module else base_name,
        f"{source_module}.{base_name}" if source_module else base_name,
        base_name,
        terminal,
    ):
        candidates.update(aliases.get(alias, []))
    return sorted(candidates)


def build_inheritance_edges(
    parsed: list[dict],
    symbols: list[dict],
    module_to_file: dict[str, str],
    resolve_import_module: ImportResolver,
) -> list[dict]:
    """Build fail-safe class inheritance/interface edges across supported languages."""
    classes = [row for row in symbols if row.get("kind") == "class"]
    class_by_id = {row["id"]: row for row in classes}
    class_by_file_qname = {(row["file"], row["qname"]): row for row in classes}
    aliases: dict[str, list[str]] = {}
    for row in classes:
        for alias in {row["id"], row["name"], row["qname"], f"{row['module']}.{row['qname']}"}:
            aliases.setdefault(alias, []).append(row["id"])
    for key in list(aliases):
        aliases[key] = sorted(set(aliases[key]))

    edges: list[dict] = []
    for doc in parsed:
        source_module = next((row["module"] for row in classes if row["file"] == doc["path"]), "")
        for item in doc.get("classes") or []:
            source_qname = item.get("qname") or item.get("name")
            source = class_by_file_qname.get((doc["path"], source_qname))
            if not source:
                continue
            raw_records = item.get("base_records") or [
                {"name": base, "relation": "inherits"} for base in item.get("bases") or []
            ]
            for record in raw_records:
                base_name = _normalize_type_name(record.get("name") or "")
                if not base_name:
                    continue
                imported = _imported_class_candidates(
                    doc,
                    base_name,
                    classes,
                    module_to_file,
                    resolve_import_module,
                )
                if len(imported) == 1:
                    candidates = imported
                    resolution = "import_exact"
                elif len(imported) > 1:
                    candidates = imported
                    resolution = "ambiguous_import"
                else:
                    candidates = _global_class_candidates(base_name, source_module, aliases)
                    resolution = "exact_or_unambiguous_alias" if len(candidates) == 1 else ("ambiguous" if candidates else "unresolved")

                target_id = candidates[0] if len(candidates) == 1 else None
                target = class_by_id.get(target_id) if target_id else None
                edges.append({
                    "source_symbol_id": source["id"],
                    "source_file": source["file"],
                    "base": base_name,
                    "relation": str(record.get("relation") or "inherits"),
                    "target_symbol_id": target_id,
                    "target_file": target.get("file") if target else None,
                    "resolution": resolution,
                    "candidate_count": len(candidates),
                    "language": doc.get("language"),
                })

    edges.sort(key=lambda row: (row["source_symbol_id"], row["relation"], row["base"]))
    return edges
