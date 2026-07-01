"""
Phase 42 similarity layer.

The old Jaccard-only implementation missed common coding intent pairs such as:
- fix login bug
- fix authentication error

This implementation combines lexical normalization, synonym expansion, sequence ratio,
and token overlap. It is dependency-free but much closer to semantic intent matching.
"""

from difflib import SequenceMatcher

SYNONYMS = {
    "auth": "authentication",
    "signin": "login",
    "sign-in": "login",
    "log-in": "login",
    "bug": "error",
    "issue": "error",
    "problem": "error",
    "db": "database",
    "query": "database_query",
    "speed": "optimize",
    "speedup": "optimize",
    "fast": "optimize",
    "slow": "optimize",
    "perf": "performance",
    "performance": "optimize",
    "api": "endpoint",
    "route": "endpoint",
}


def _normalize(text):
    tokens = []
    for raw in str(text or "").lower().replace("/", " ").replace("_", " ").replace("-", " ").split():
        token = "".join(ch for ch in raw if ch.isalnum())
        if not token:
            continue
        token = SYNONYMS.get(token, token)
        tokens.append(token)
    return tokens


def token_overlap(a, b):
    aa = set(_normalize(a))
    bb = set(_normalize(b))
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa | bb)


def jaccard(a, b):
    """
    Backward-compatible API for existing llm_cache.py.

    Phase 42 improves similarity beyond plain Jaccard, but older modules still
    import `jaccard`. Keep the public function name and route it to the improved
    semantic similarity implementation.
    """
    return semantic_similarity(a, b)


def semantic_similarity(a, b):
    aa = _normalize(a)
    bb = _normalize(b)
    if not aa or not bb:
        return 0.0

    overlap = token_overlap(a, b)
    seq = SequenceMatcher(None, " ".join(aa), " ".join(bb)).ratio()

    # Intent boosts for common coding task categories.
    boost = 0.0
    pairs = [set(aa), set(bb)]
    if any("login" in x for x in pairs) and any("authentication" in x for x in pairs):
        boost += 0.35
    if any("optimize" in x for x in pairs) and any("database" in x or "database_query" in x for x in pairs):
        boost += 0.30
    if any("endpoint" in x for x in pairs):
        boost += 0.10

    return min(1.0, max(overlap, seq * 0.7 + overlap * 0.3 + boost))


def similar_enough(a, b, threshold=0.65):
    return semantic_similarity(a, b) >= threshold
