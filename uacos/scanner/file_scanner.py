from pathlib import Path
from datetime import datetime, timezone
from uacos.scanner.ignore_rules import should_index_file
from uacos.scanner.language import detect_language
from uacos.scanner.hash_cache import sha256_file, read_text_safely
from uacos.storage import connect
from uacos.codeintel.symbol_parser import extract_symbols

IGNORED_PARENT_DIRS = {".git", ".uacos", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def iter_candidate_files(repo_root: Path):
    for path in repo_root.rglob("*"):
        if path.is_dir():
            continue
        rel_parts = path.relative_to(repo_root).parts
        if any(part in IGNORED_PARENT_DIRS for part in rel_parts[:-1]):
            continue
        yield path

def _replace_symbols(conn, file_id: int, rel: str, language: str, symbols) -> int:
    conn.execute("DELETE FROM symbols WHERE file_id = ?", (file_id,))
    conn.execute("DELETE FROM symbols_fts WHERE rowid NOT IN (SELECT id FROM symbols)")
    count = 0
    for sym in symbols:
        score = 2.0 if sym.kind in {"class", "function", "struct", "interface"} else 1.0
        cur = conn.execute(
            '''
            INSERT INTO symbols(file_id, path, name, kind, language, start_line, end_line, signature, score)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (file_id, rel, sym.name, sym.kind, language, sym.start_line, sym.end_line, sym.signature, score),
        )
        sid = cur.lastrowid
        conn.execute(
            "INSERT INTO symbols_fts(rowid, name, kind, path, signature) VALUES(?, ?, ?, ?, ?)",
            (sid, sym.name, sym.kind, rel, sym.signature or ""),
        )
        count += 1
    return count

def scan_repo(repo_root: Path) -> dict:
    conn = connect(repo_root)
    started = utcnow()
    cur = conn.execute("INSERT INTO scan_runs(started_at, repo_path) VALUES(?, ?)", (started, str(repo_root)))
    scan_run_id = cur.lastrowid
    files_seen = files_indexed = files_skipped = files_changed = symbols_indexed = 0
    changed_files = []

    for path in iter_candidate_files(repo_root):
        files_seen += 1
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        ok, reason = should_index_file(path)
        if not ok:
            files_skipped += 1
            conn.execute("INSERT INTO skipped_files(scan_run_id, path, reason) VALUES(?, ?, ?)", (scan_run_id, rel, reason))
            continue
        try:
            stat = path.stat()
            digest = sha256_file(path)
            language = detect_language(path)
            existing = conn.execute("SELECT id, sha256 FROM files WHERE path = ?", (rel,)).fetchone()
            changed = existing is None or existing["sha256"] != digest
            if changed:
                changed_files.append(rel)
                content = read_text_safely(path)
                conn.execute(
                    '''
                    INSERT INTO files(path, sha256, mtime, language, size_bytes, last_indexed_at)
                    VALUES(?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        sha256=excluded.sha256,
                        mtime=excluded.mtime,
                        language=excluded.language,
                        size_bytes=excluded.size_bytes,
                        last_indexed_at=excluded.last_indexed_at
                    ''',
                    (rel, digest, stat.st_mtime, language, stat.st_size, utcnow()),
                )
                conn.execute("DELETE FROM files_fts WHERE rowid IN (SELECT id FROM files WHERE path = ?)", (rel,))
                file_id = conn.execute("SELECT id FROM files WHERE path = ?", (rel,)).fetchone()["id"]
                conn.execute("INSERT INTO files_fts(rowid, path, language, content) VALUES(?, ?, ?, ?)", (file_id, rel, language, content))
                symbols_indexed += _replace_symbols(conn, file_id, rel, language, extract_symbols(content, language))
                files_changed += 1
            else:
                file_id = existing["id"]
                symbols_indexed += conn.execute("SELECT COUNT(*) AS c FROM symbols WHERE file_id = ?", (file_id,)).fetchone()["c"]
            files_indexed += 1
        except Exception as exc:
            files_skipped += 1
            conn.execute("INSERT INTO skipped_files(scan_run_id, path, reason) VALUES(?, ?, ?)", (scan_run_id, rel, f"error:{type(exc).__name__}:{exc}"))

    conn.execute(
        '''
        UPDATE scan_runs
        SET finished_at=?, files_seen=?, files_indexed=?, files_skipped=?, files_changed=?, symbols_indexed=?
        WHERE id=?
        ''',
        (utcnow(), files_seen, files_indexed, files_skipped, files_changed, symbols_indexed, scan_run_id),
    )
    conn.commit()
    conn.close()
    return {
        "scan_run_id": scan_run_id,
        "files_seen": files_seen,
        "files_indexed": files_indexed,
        "files_skipped": files_skipped,
        "files_changed": files_changed,
        "changed_files": changed_files,
        "symbols_indexed": symbols_indexed,
        "started_at": started,
        "finished_at": utcnow(),
    }
