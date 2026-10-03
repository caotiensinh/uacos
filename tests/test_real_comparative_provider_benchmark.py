from pathlib import Path
import sys

from uacos.benchmarks.real_provider import build_mode_context, run_real_comparative_suite


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
 def target():
-    return 1
+    return 2
"""


def _fake_codex(path: Path) -> Path:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "_ = sys.stdin.read()\n"
        f"sys.stdout.write({PATCH!r})\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def target():\n    return 1\n", encoding="utf-8")
    (repo / "README.md").write_text("Target application documentation.\n", encoding="utf-8")
    (repo / "config.yaml").write_text("feature_toggle: target\n", encoding="utf-8")
    (repo / "generated").mkdir()
    (repo / "generated" / "generated_config.yaml").write_text("feature_toggle: target\n", encoding="utf-8")
    (repo / "vendor").mkdir()
    (repo / "vendor" / "foreign.md").write_text("target vendor documentation\n", encoding="utf-8")
    for index in range(8):
        (repo / f"noise_{index}.py").write_text(
            "\n".join(f"NOISE_{index}_{line} = {line}" for line in range(80)) + "\n",
            encoding="utf-8",
        )
    return repo


def test_mode_contexts_are_distinct_and_traceable(tmp_path: Path):
    repo = _repo(tmp_path)
    task = "Update target so it returns 2"
    full_repo = build_mode_context(repo, task, "full_repo", full_repo_max_chars=500000)
    grep = build_mode_context(repo, task, "grep")
    uacos = build_mode_context(repo, task, "uacos")

    assert full_repo["truncated"] is False
    assert "app:target" in full_repo["selected_symbols"]
    assert "README.md" in full_repo["selected_files"]
    assert "config.yaml" in full_repo["selected_files"]
    assert "generated/generated_config.yaml" not in full_repo["selected_files"]
    assert "vendor/foreign.md" not in full_repo["selected_files"]
    assert "app.py" in grep["selected_files"]
    assert "app:target" in grep["selected_symbols"]
    assert "app.py" in uacos["selected_files"]
    assert "app:target" in uacos["selected_symbols"]
    assert full_repo["input_tokens_est"] > uacos["input_tokens_est"]


def test_grep_baseline_can_find_non_graph_config_text(tmp_path: Path):
    repo = _repo(tmp_path)
    grep = build_mode_context(repo, "Change feature_toggle target", "grep")
    assert "config.yaml" in grep["selected_files"]
    assert "generated/generated_config.yaml" not in grep["selected_files"]
    assert "vendor/foreign.md" not in grep["selected_files"]


def test_real_comparative_suite_runs_same_provider_three_modes_three_repeats(tmp_path: Path):
    repo = _repo(tmp_path)
    fake = _fake_codex(tmp_path / "codex")
    manifest = {
        "version": 1,
        "repeats": 3,
        "tasks": [
            {
                "id": "target-return",
                "repo": str(repo),
                "task": "Update target so it returns 2",
                "allowed_files": ["app.py"],
                "tests": [
                    f"{sys.executable} -c \"import app; assert app.target() == 2\""
                ],
                "required_symbols": ["app:target"],
                "required_relations": [],
                "max_iterations": 1,
            }
        ],
    }

    result = run_real_comparative_suite(
        manifest,
        provider="codex",
        argv=[str(fake)],
        model="fixture-model",
        output_dir=tmp_path / "out",
    )

    assert result["status"] == "pass"
    report = result["report"]
    assert report["real_provider_execution"] is True
    assert report["provider"] == "codex"
    assert report["model"] == "fixture-model"
    assert len(report["observations"]) == 9
    assert all(row["passed"] for row in report["observations"])
    assert all(row["provider"] == "codex" for row in report["observations"])
    assert all(row["model"] == "fixture-model" for row in report["observations"])
    assert report["summaries"]["uacos"]["required_symbol_recall"] == 1.0
    assert Path(result["report_path"]).is_file()
    assert Path(result["observations_path"]).is_file()
    assert Path(result["evidence_path"]).is_file()


def test_real_comparative_suite_refuses_less_than_three_repeats(tmp_path: Path):
    repo = _repo(tmp_path)
    fake = _fake_codex(tmp_path / "codex")
    manifest = {
        "version": 1,
        "repeats": 2,
        "tasks": [{"id": "x", "repo": str(repo), "task": "Update target"}],
    }
    try:
        run_real_comparative_suite(
            manifest,
            provider="codex",
            argv=[str(fake)],
            model="fixture-model",
            output_dir=tmp_path / "out",
        )
    except ValueError as exc:
        assert str(exc) == "real_comparative_minimum_repeats_is_3"
    else:
        raise AssertionError("expected minimum repeat validation")
