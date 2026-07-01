from __future__ import annotations

from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.skill.store import add_skill
from uacos.memory.store import add_memory
from uacos.semantic.search import build_semantic_index, semantic_search, semantic_context
from uacos.retrieval.context_pack import build_context_pack

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        init_storage(repo)
        scan_repo(repo)
        skill = add_skill(
            repo,
            title="Fix Python venv mismatch",
            problem_signatures=["unsupported operand type", "NoneType", "Python39", "str | None"],
            root_cause="Old Python runtime cannot parse modern union syntax.",
            solution_steps=["Recreate venv with Python 3.12"],
            commands=["py -3.12 -m venv .venv"],
            category="python_env",
            status="approved",
            confidence=0.95,
        )
        mem = add_memory(
            repo,
            kind="project_truth",
            key="barrier_safety_roi",
            value="Lower barrier must obey safe ROI and avoid hitting vehicles.",
            tags=["barrier", "safety", "roi"],
        )
        idx = build_semantic_index(repo)
        assert idx["doc_count"] >= 2
        res = semantic_search(repo, "old python none type union syntax error", limit=5)
        assert res["results"]
        assert any(r["id"] == skill["id"] for r in res["results"])
        mem_res = semantic_search(repo, "gate lower safe vehicle roi", limit=5)
        assert any(r["id"] == mem["id"] for r in mem_res["results"])
        ctx = semantic_context(repo, "python unsupported union syntax")
        assert "Fix Python venv mismatch" in ctx
        pack = build_context_pack(repo, "python unsupported union syntax", max_tokens=3500)
        assert "Semantic Memory Search" in pack["content"]
        assert "Fix Python venv mismatch" in pack["content"]
        print("PHASE14_SMOKE_OK")
        print("index_docs=", idx["doc_count"])
        print("top=", res["results"][0]["title"])

if __name__ == "__main__":
    main()
