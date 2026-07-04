from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from uacos.search import search_repo
from uacos.codeintel.repo_map import get_repo_map, estimate_tokens
from uacos.codeintel.snippet import extract_snippet
from uacos.storage import connect
from uacos.memory.store import memory_summary_for_task
from uacos.skill.store import skill_summary_for_task
from uacos.semantic.search import semantic_context
from uacos.impact.analyzer import impact_by_task

def _now():
    return datetime.now(timezone.utc).isoformat()

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def build_context_pack(repo_root: Path, task: str, max_tokens: int = 3500, search_limit: int = 8) -> dict:
    hits = search_repo(repo_root, task, limit=search_limit)
    repo_map = get_repo_map(repo_root, query=task, max_tokens=max(800, max_tokens // 2))
    try:
        impact = impact_by_task(repo_root, task, limit=search_limit)
        impact_ranked_files = impact.get("impacted_files", [])
    except Exception:
        impact_ranked_files = []
    snippets = []

    conn = connect(repo_root)
    for hit in hits[:5]:
        row = conn.execute(
            "SELECT start_line, end_line FROM symbols WHERE path = ? ORDER BY start_line LIMIT 1",
            (hit["path"],),
        ).fetchone()
        try:
            if row:
                snippets.append(extract_snippet(repo_root, hit["path"], row["start_line"], row["end_line"], context=2))
            else:
                snippets.append(extract_snippet(repo_root, hit["path"], 1, 40, context=0))
        except Exception as exc:
            snippets.append({"path": hit["path"], "error": str(exc), "content": ""})
    conn.close()

    parts = [
        "# UACOS Context Pack v0",
        "",
        "## Task",
        task,
        "",
        "## Relevant Memory",
        memory_summary_for_task(repo_root, task),
        "",
        "## Relevant Skills",
        skill_summary_for_task(repo_root, task),
        "",
        "## Semantic Memory Search",
        semantic_context(repo_root, task),
        "",
        "## Operating Rules",
        "- Use this context instead of reading the whole repository.",
        "- Do not access secret-like files such as `.env`, `*.pem`, `*.key`.",
        "- Ask for scope expansion if more files are required.",
        "- Do not claim DONE without tests or explicit validation evidence.",
        "- Prefer touching files from the Impact Analysis ranking below. If a change requires a file not listed there, say why before editing it.",
        "",
        "## Impact Analysis",
        "Files ranked by dependency-graph and symbol relevance to this task (highest first):",
    ]
    if impact_ranked_files:
        for row in impact_ranked_files:
            reasons = ",".join(row.get("reasons", [])) or "n/a"
            parts.append(f"- `{row['file']}` score={row['score']} reasons={reasons}")
    else:
        parts.append("- (no graph-based impact ranking available for this task)")
    parts += [
        "",
        "## Repo Map",
        repo_map,
        "",
        "## Search Hits",
    ]
    for hit in hits:
        parts.append(f"- `{hit['path']}` ({hit['language']}, {hit['size_bytes']} bytes): {hit.get('snippet', '')}")

    parts += ["", "## Snippets"]
    for snip in snippets:
        parts.append(f"### {snip.get('path')}")
        if snip.get("error"):
            parts.append(f"ERROR: {snip['error']}")
        else:
            parts.append("```text")
            parts.append(snip.get("content", ""))
            parts.append("```")
        parts.append("")

    content = "\n".join(parts).strip() + "\n"
    if estimate_tokens(content) > max_tokens:
        content = content[: max_tokens * 4] + "\n\n_Context pack truncated by token budget._\n"

    files_hash = _hash(json.dumps(hits, sort_keys=True, ensure_ascii=False))
    rules_hash = _hash("phase2-default-rules-v0")
    memory_hash = _hash("phase2-no-memory-yet")
    context_id = _hash(task + files_hash + rules_hash + memory_hash)[:24]
    token_count = estimate_tokens(content)

    conn = connect(repo_root)
    conn.execute(
        '''
        INSERT OR REPLACE INTO context_packs(id, task, files_hash, rules_hash, memory_hash, content, token_count, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (context_id, task, files_hash, rules_hash, memory_hash, content, token_count, _now()),
    )
    conn.commit()
    conn.close()
    return {"id": context_id, "task": task, "token_count": token_count, "content": content, "search_hits": hits, "impact_ranked_files": impact_ranked_files}
