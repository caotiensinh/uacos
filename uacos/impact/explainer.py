from __future__ import annotations

from pathlib import Path
import re

from uacos.compression.engine import load_compression_cache
from uacos.impact.analyzer import impact_by_task


ROLE_HINTS = [
    ("test", ("test", "tests/", "_test.", "spec.")),
    ("documentation", ("docs/", "readme", ".md")),
    ("configuration", ("config", "settings", ".yaml", ".yml", ".json", "pyproject.toml")),
    ("api_or_route", ("api", "route", "router", "endpoint", "controller")),
    ("security_or_auth", ("auth", "login", "permission", "rbac", "token", "secret")),
    ("cli_or_command", ("cli", "command", "argparse")),
    ("workflow_or_ci", (".github/workflows", "release_gate", "ci")),
]

GENERIC_REASON_LABELS = {
    "keyword_search": "task keywords matched this file through repository search",
}


def _task_terms(task: str) -> list[str]:
    return sorted({term.lower() for term in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", task or "")})[:30]


def _path_roles(path: str) -> list[str]:
    low = (path or "").lower()
    roles = []
    for role, needles in ROLE_HINTS:
        if any(needle in low for needle in needles):
            roles.append(role)
    if not roles:
        roles.append("source_or_project_file")
    return roles


def _summarize_reason(reason: str) -> str:
    if reason.startswith("symbol:"):
        return "symbol match from task: " + reason.split(":", 1)[1]
    return GENERIC_REASON_LABELS.get(reason, reason)


def explain_selected_files(repo_root: Path, task: str, selected_files: list[dict], impact: dict | None = None, cache: dict | None = None) -> dict:
    """Explain why the currently selected context files are relevant.

    This is intentionally a transparent heuristic layer. It does not change which
    files compressed_context selected; it only adds reviewable reasons so users can
    spot weak context selection before giving the context to an AI agent.
    """

    impact = impact or impact_by_task(repo_root, task, limit=max(20, len(selected_files) * 2 or 10))
    cache = cache or load_compression_cache(repo_root)
    impact_rows = {row.get("file"): row for row in impact.get("impacted_files", [])}
    cache_files = cache.get("files", {})
    task_terms = _task_terms(task)

    explanations = []
    for selected in selected_files or []:
        rel = selected.get("file") or selected.get("path")
        if not rel:
            continue
        impact_row = impact_rows.get(rel, {})
        cache_row = cache_files.get(rel, {})
        raw_reasons = impact_row.get("reasons") or []
        readable_reasons = [_summarize_reason(reason) for reason in raw_reasons]
        if selected.get("score") is not None:
            readable_reasons.append(f"impact score {selected.get('score')}")
        if cache_row.get("kind"):
            readable_reasons.append(f"summary kind: {cache_row.get('kind')}")
        if cache_row.get("raw_tokens_est") and cache_row.get("summary_tokens_est"):
            readable_reasons.append(
                f"token tradeoff: raw {cache_row.get('raw_tokens_est')} -> summary {cache_row.get('summary_tokens_est')}"
            )
        roles = _path_roles(rel)
        matched_terms = [term for term in task_terms if term in rel.lower() or term in " ".join(raw_reasons).lower()]
        confidence = "high" if raw_reasons and selected.get("score", 0) >= 1.0 else "medium" if raw_reasons or selected.get("score", 0) >= 0.5 else "low"
        explanations.append({
            "file": rel,
            "confidence": confidence,
            "roles": roles,
            "matched_task_terms": matched_terms,
            "reasons": readable_reasons or ["selected by compression context but no detailed reason was available"],
            "impact_score": selected.get("score") or impact_row.get("score"),
            "raw_tokens_est": selected.get("raw_tokens") or cache_row.get("raw_tokens_est"),
            "summary_tokens_est": selected.get("summary_tokens") or cache_row.get("summary_tokens_est"),
            "quality_note": "review this file if confidence is low or the role does not match the task intent",
        })

    low_confidence = [row["file"] for row in explanations if row["confidence"] == "low"]
    return {
        "status": "ok",
        "task": task,
        "explained_file_count": len(explanations),
        "low_confidence_files": low_confidence,
        "task_terms": task_terms,
        "explanations": explanations,
        "claim": "Selection explanations are heuristic review signals. They do not prove the selected context is complete or correct.",
    }
