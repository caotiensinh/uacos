from __future__ import annotations

from uacos.graph.roles import is_test_path, semantic_file_role


def build_architecture_edges(parsed: list[dict], call_edges: list[dict], symbol_by_id: dict[str, dict]) -> list[dict]:
    edges: list[dict] = []
    seen: set[tuple] = set()

    for doc in parsed:
        file_path = str(doc.get("path") or "")
        module_symbols = {
            str(row.get("qname") or row.get("name") or ""): row
            for group in (doc.get("functions", []), doc.get("async_functions", []), doc.get("methods", []))
            for row in group
        }
        for route in doc.get("routes", []) or []:
            handler = str(route.get("handler") or "")
            symbol = module_symbols.get(handler)
            key = ("route_to_handler", file_path, handler, route.get("method"), route.get("path"))
            if key in seen:
                continue
            seen.add(key)
            edges.append({
                "kind": "route_to_handler",
                "source": f"{route.get('method') or 'ROUTE'} {route.get('path') or '?'}",
                "source_file": file_path,
                "target_symbol_qname": handler,
                "target_file": file_path,
                "lineno": route.get("lineno") or (symbol or {}).get("lineno"),
                "method": route.get("method"),
                "path": route.get("path"),
                "resolution": "declared_route",
            })

    handler_symbols = {
        edge.get("target_symbol_qname")
        for edge in edges
        if edge.get("kind") == "route_to_handler"
    }

    for edge in call_edges:
        source_id = edge.get("source_symbol_id")
        target_id = edge.get("target_symbol_id")
        if not source_id or not target_id:
            continue
        source = symbol_by_id.get(source_id) or {}
        target = symbol_by_id.get(target_id) or {}
        source_qname = str(source.get("qname") or "")
        source_role = semantic_file_role(str(source.get("file") or ""))
        target_role = semantic_file_role(str(target.get("file") or ""))

        kind = None
        if source_qname in handler_symbols and target_role == "service":
            kind = "handler_to_service"
        elif source_role == "service" and target_role == "database":
            kind = "service_to_database"
        if not kind:
            continue
        key = (kind, source_id, target_id)
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "kind": kind,
            "source_symbol_id": source_id,
            "target_symbol_id": target_id,
            "source_file": source.get("file"),
            "target_file": target.get("file"),
            "resolution": edge.get("resolution"),
            "lineno": edge.get("lineno"),
        })

    return edges


def build_test_dependency_edges(file_edges: list[dict], call_edges: list[dict]) -> list[dict]:
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for edge in file_edges:
        source = str(edge.get("source") or "")
        target = str(edge.get("target") or "")
        if not source or not target or not is_test_path(source) or is_test_path(target):
            continue
        key = (source, target, "import")
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "kind": "test_to_production",
            "source_file": source,
            "target_file": target,
            "evidence": "import",
            "language": edge.get("language"),
        })

    for edge in call_edges:
        source = str(edge.get("source_file") or "")
        target = str(edge.get("target_file") or "")
        if not source or not target or not is_test_path(source) or is_test_path(target):
            continue
        key = (source, target, "call")
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "kind": "test_to_production",
            "source_file": source,
            "target_file": target,
            "source_symbol_id": edge.get("source_symbol_id"),
            "target_symbol_id": edge.get("target_symbol_id"),
            "evidence": "call",
            "language": edge.get("language"),
        })

    return edges
