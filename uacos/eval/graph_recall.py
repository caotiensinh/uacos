from __future__ import annotations


def _edge_key(edge: dict) -> tuple:
    return (
        str(edge.get("kind") or ""),
        str(edge.get("source_symbol_id") or edge.get("source_file") or edge.get("source") or ""),
        str(edge.get("target_symbol_id") or edge.get("target_file") or edge.get("target_symbol_qname") or ""),
    )


def evaluate_graph_recall(
    graph: dict,
    required_symbol_ids: list[str],
    required_relations: list[dict],
    min_symbol_recall: float = 0.95,
    min_relation_recall: float = 0.90,
) -> dict:
    actual_symbols = {str(row.get("id") or "") for row in graph.get("symbols", []) or []}
    actual_edges = set()
    for collection in (
        "file_edges",
        "call_edges",
        "inheritance_edges",
        "architecture_edges",
        "test_dependency_edges",
    ):
        for edge in graph.get(collection, []) or []:
            actual_edges.add(_edge_key(edge))

    required_symbols = {str(value) for value in required_symbol_ids if str(value)}
    required_edge_keys = {_edge_key(edge) for edge in required_relations}
    missing_symbols = sorted(required_symbols - actual_symbols)
    missing_relations = sorted(required_edge_keys - actual_edges)

    symbol_recall = 1.0 if not required_symbols else (len(required_symbols) - len(missing_symbols)) / len(required_symbols)
    relation_recall = 1.0 if not required_edge_keys else (len(required_edge_keys) - len(missing_relations)) / len(required_edge_keys)
    passed = symbol_recall >= min_symbol_recall and relation_recall >= min_relation_recall

    return {
        "passed": passed,
        "symbol_recall": round(symbol_recall, 6),
        "relation_recall": round(relation_recall, 6),
        "required_symbol_count": len(required_symbols),
        "required_relation_count": len(required_edge_keys),
        "missing_symbol_ids": missing_symbols,
        "missing_relations": [list(row) for row in missing_relations],
        "thresholds": {
            "min_symbol_recall": min_symbol_recall,
            "min_relation_recall": min_relation_recall,
        },
    }
