from pathlib import Path
from uacos.storage import connect

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def _match_query(query: str) -> str:
    tokens = [t.strip() for t in query.replace('"', " ").split() if t.strip()]
    return " OR ".join(tokens)

def get_repo_map(repo_root: Path, query=None, max_tokens: int = 1800, limit: int = 80) -> str:
    conn = connect(repo_root)
    rows = []
    if query and query.strip():
        try:
            rows = conn.execute(
                '''
                SELECT s.path, s.name, s.kind, s.start_line, s.end_line, s.signature, s.score
                FROM symbols_fts
                JOIN symbols s ON s.id = symbols_fts.rowid
                WHERE symbols_fts MATCH ?
                ORDER BY s.score DESC, s.path, s.start_line
                LIMIT ?
                ''',
                (_match_query(query), limit),
            ).fetchall()
        except Exception:
            rows = []

    if not rows:
        rows = conn.execute(
            '''
            SELECT path, name, kind, start_line, end_line, signature, score
            FROM symbols
            ORDER BY score DESC, path, start_line
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    conn.close()

    by_file = {}
    for r in rows:
        by_file.setdefault(r["path"], []).append(r)

    out = ["# Repo Map", "", f"Query: {query or '(top symbols)'}", ""]
    for path, items in sorted(by_file.items()):
        out.append(f"## {path}")
        for r in items:
            out.append(f"- L{r['start_line']}-L{r['end_line']} `{r['kind']}` **{r['name']}** — {r['signature'] or ''}")
        out.append("")
        if estimate_tokens("\n".join(out)) > max_tokens:
            out.append("_Repo map truncated by token budget._")
            break
    return "\n".join(out).strip() + "\n"
