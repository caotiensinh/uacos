from pathlib import Path
import sqlite3
from uacos.config import db_path, uacos_dir

SCHEMA = '''
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    sha256 TEXT NOT NULL,
    mtime REAL NOT NULL,
    language TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    is_generated INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'normal',
    summary TEXT,
    last_indexed_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
    path,
    language,
    content,
    content='',
    tokenize='unicode61'
);

CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    language TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    signature TEXT,
    score REAL DEFAULT 1.0,
    FOREIGN KEY(file_id) REFERENCES files(id)
);

CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_path ON symbols(path);

CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5(
    name,
    kind,
    path,
    signature,
    content='',
    tokenize='unicode61'
);

CREATE TABLE IF NOT EXISTS context_packs (
    id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    files_hash TEXT NOT NULL,
    rules_hash TEXT NOT NULL,
    memory_hash TEXT NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    repo_path TEXT NOT NULL,
    files_seen INTEGER DEFAULT 0,
    files_indexed INTEGER DEFAULT 0,
    files_skipped INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    symbols_indexed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS skipped_files (
    id INTEGER PRIMARY KEY,
    scan_run_id INTEGER,
    path TEXT NOT NULL,
    reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
'''

def connect(repo_root: Path) -> sqlite3.Connection:
    d = uacos_dir(repo_root)
    d.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path(repo_root))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn

def init_storage(repo_root: Path) -> Path:
    conn = connect(repo_root)
    conn.execute("INSERT OR REPLACE INTO kv(key, value) VALUES('schema_version', '2')")
    conn.commit()
    conn.close()
    return db_path(repo_root)
