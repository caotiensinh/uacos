from pathlib import Path
from uacos.storage import connect

def _match_query(query: str, mode: str = "AND") -> str:
    # Quote every token for FTS5 safety. Raw task text may include =, -, :, /, etc.
    tokens = [t.strip() for t in query.split() if t.strip()]
    safe = []
    for t in tokens:
        t = t.replace('"', '""')
        safe.append('"' + t + '"')
    return f" {mode} ".join(safe)

def search_repo(repo_root: Path, query: str, limit: int = 20) -> list:
    conn = connect(repo_root)
    if not query.strip():
        return []
    try:
        rows = conn.execute(
            '''
            SELECT f.path, f.language, f.size_bytes,
                   snippet(files_fts, 2, '[', ']', ' ... ', 12) AS snippet,
                   bm25(files_fts) AS rank
            FROM files_fts
            JOIN files f ON f.id = files_fts.rowid
            WHERE files_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            ''',
            (_match_query(query, "AND"), limit),
        ).fetchall()
    except Exception:
        rows = conn.execute(
            '''
            SELECT f.path, f.language, f.size_bytes,
                   snippet(files_fts, 2, '[', ']', ' ... ', 12) AS snippet,
                   bm25(files_fts) AS rank
            FROM files_fts
            JOIN files f ON f.id = files_fts.rowid
            WHERE files_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            ''',
            (_match_query(query, "OR"), limit),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_symbols(repo_root: Path, query=None, limit: int = 50) -> list:
    conn = connect(repo_root)
    if query and query.strip():
        try:
            rows = conn.execute(
                '''
                SELECT s.path, s.name, s.kind, s.language, s.start_line, s.end_line, s.signature, s.score
                FROM symbols_fts
                JOIN symbols s ON s.id = symbols_fts.rowid
                WHERE symbols_fts MATCH ?
                ORDER BY s.score DESC, s.path, s.start_line
                LIMIT ?
                ''',
                (_match_query(query, "OR"), limit),
            ).fetchall()
        except Exception:
            rows = []
    else:
        rows = conn.execute(
            '''
            SELECT path, name, kind, language, start_line, end_line, signature, score
            FROM symbols
            ORDER BY score DESC, path, start_line
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def stats(repo_root: Path) -> dict:
    conn = connect(repo_root)
    file_count = conn.execute("SELECT COUNT(*) AS c FROM files").fetchone()["c"]
    symbol_count = conn.execute("SELECT COUNT(*) AS c FROM symbols").fetchone()["c"]
    lang_rows = conn.execute("SELECT language, COUNT(*) AS c FROM files GROUP BY language ORDER BY c DESC").fetchall()
    kind_rows = conn.execute("SELECT kind, COUNT(*) AS c FROM symbols GROUP BY kind ORDER BY c DESC").fetchall()
    last_scan = conn.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return {
        "file_count": file_count,
        "symbol_count": symbol_count,
        "languages": [dict(r) for r in lang_rows],
        "symbol_kinds": [dict(r) for r in kind_rows],
        "last_scan": dict(last_scan) if last_scan else None,
    }
