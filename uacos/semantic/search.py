from __future__ import annotations

from pathlib import Path
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from uacos.config import uacos_dir
from uacos.memory.store import read_memories
from uacos.skill.store import read_skills

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "is", "are", "was", "were",
    "this", "that", "it", "as", "be", "by", "from", "at", "if", "then", "than", "into", "not", "no",
    "cua", "la", "va", "cho", "voi", "khi", "neu", "thi", "khong", "trong", "mot",
    "です", "ます"
}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def semantic_index_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "semantic_index.json"

def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9_\-\.]+|[\u3040-\u30ff\u3400-\u9fff]+", text.lower())
    tokens = []
    for tok in raw:
        tok = tok.strip("._-")
        if len(tok) < 2:
            continue
        if tok in STOPWORDS:
            continue
        tokens.append(tok)
    # Add light character 3-grams for fuzzy matching on technical tokens.
    grams = []
    for tok in tokens:
        if len(tok) >= 5 and re.match(r"^[a-z0-9_\-\.]+$", tok):
            grams.extend([tok[i:i+3] for i in range(0, len(tok)-2)])
    return tokens + grams

def _skill_text(skill: dict) -> str:
    fields = [
        skill.get("title", ""),
        skill.get("category", ""),
        " ".join(skill.get("problem_signatures", [])),
        skill.get("root_cause", ""),
        " ".join(skill.get("solution_steps", [])),
        " ".join(skill.get("commands", [])),
        " ".join(skill.get("verification", [])),
        " ".join(skill.get("applies_to", [])),
        " ".join(skill.get("tags", [])),
        skill.get("status", ""),
    ]
    return "\n".join(str(x) for x in fields if x)

def _memory_text(memory: dict) -> str:
    fields = [
        memory.get("kind", ""),
        memory.get("key", ""),
        memory.get("value", ""),
        " ".join(memory.get("tags", [])),
        " ".join(memory.get("applies_to", [])),
        memory.get("source", ""),
    ]
    return "\n".join(str(x) for x in fields if x)

def collect_semantic_documents(repo_root: Path, include_inactive: bool = False) -> list[dict]:
    docs = []
    for skill in read_skills(repo_root, include_inactive=include_inactive):
        docs.append({
            "id": skill["id"],
            "type": "skill",
            "title": skill.get("title", skill["id"]),
            "status": skill.get("status"),
            "text": _skill_text(skill),
            "payload": skill,
        })
    for mem in read_memories(repo_root, include_invalid=include_inactive):
        docs.append({
            "id": mem["id"],
            "type": "memory",
            "title": mem.get("key", mem["id"]),
            "status": "invalid" if mem.get("invalid_at") else "active",
            "text": _memory_text(mem),
            "payload": mem,
        })
    return docs

def _tf(tokens: list[str]) -> dict[str, float]:
    c = Counter(tokens)
    if not c:
        return {}
    max_count = max(c.values())
    return {k: v / max_count for k, v in c.items()}

def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in common)
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def build_semantic_index(repo_root: Path, include_inactive: bool = False) -> dict:
    docs = collect_semantic_documents(repo_root, include_inactive=include_inactive)
    tokenized = []
    df = defaultdict(int)
    for d in docs:
        toks = tokenize(d["text"])
        tokenized.append(toks)
        for t in set(toks):
            df[t] += 1
    n = max(len(docs), 1)
    idf = {t: math.log((1 + n) / (1 + freq)) + 1.0 for t, freq in df.items()}
    index_docs = []
    for doc, toks in zip(docs, tokenized):
        tf = _tf(toks)
        vector = {t: round(tf[t] * idf.get(t, 1.0), 8) for t in tf}
        index_docs.append({
            "id": doc["id"],
            "type": doc["type"],
            "title": doc["title"],
            "status": doc["status"],
            "vector": vector,
            "payload": doc["payload"],
        })
    index = {
        "version": 1,
        "provider": "local_tfidf",
        "created_at": utcnow(),
        "doc_count": len(index_docs),
        "vocab_count": len(idf),
        "idf": idf,
        "docs": index_docs,
    }
    semantic_index_path(repo_root).write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "index_file": str(semantic_index_path(repo_root)), "doc_count": len(index_docs), "vocab_count": len(idf), "provider": "local_tfidf"}

def load_semantic_index(repo_root: Path, auto_build: bool = True) -> dict:
    path = semantic_index_path(repo_root)
    if not path.exists():
        if not auto_build:
            raise FileNotFoundError(f"semantic index not found: {path}")
        build_semantic_index(repo_root)
    return json.loads(path.read_text(encoding="utf-8"))

def _query_vector(index: dict, query: str) -> dict[str, float]:
    toks = tokenize(query)
    tf = _tf(toks)
    idf = index.get("idf", {})
    return {t: tf[t] * idf.get(t, 1.0) for t in tf}

def semantic_search(repo_root: Path, query: str, limit: int = 10, doc_type: str | None = None, min_score: float = 0.01) -> dict:
    index = load_semantic_index(repo_root, auto_build=True)
    qv = _query_vector(index, query)
    results = []
    for doc in index.get("docs", []):
        if doc_type and doc.get("type") != doc_type:
            continue
        score = _cosine(qv, doc.get("vector", {}))
        # Add tiny exact-title boost.
        if query.lower() in doc.get("title", "").lower():
            score += 0.05
        if score >= min_score:
            results.append({
                "id": doc["id"],
                "type": doc["type"],
                "title": doc["title"],
                "status": doc.get("status"),
                "score": round(score, 6),
                "payload": doc.get("payload"),
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return {"status": "ok", "query": query, "provider": index.get("provider"), "results": results[:limit], "index_doc_count": index.get("doc_count", 0)}

def semantic_context(repo_root: Path, task: str, limit: int = 8) -> str:
    result = semantic_search(repo_root, task, limit=limit, min_score=0.01)
    rows = result["results"]
    if not rows:
        return "# Semantic Memory Search\n\nNo semantic memory/skill matches found.\n"
    lines = ["# Semantic Memory Search", ""]
    for r in rows:
        lines.append(f"- [{r['type']}] {r['title']} (id={r['id']}, score={r['score']})")
        payload = r.get("payload") or {}
        if r["type"] == "skill":
            sig = payload.get("problem_signatures", [])[:3]
            sol = payload.get("solution_steps", [])[:3]
            if sig:
                lines.append("  - signatures: " + "; ".join(sig))
            if sol:
                lines.append("  - solution: " + "; ".join(sol))
        elif r["type"] == "memory":
            val = str(payload.get("value", ""))[:240]
            if val:
                lines.append("  - memory: " + val)
    return "\n".join(lines) + "\n"
