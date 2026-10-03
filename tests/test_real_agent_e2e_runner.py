from pathlib import Path

from uacos.agent.real_e2e import run_real_provider_e2e, run_real_provider_matrix


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
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


def test_real_e2e_runner_executes_cli_and_persists_evidence(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    fake = _fake_codex(tmp_path / "codex")

    result = run_real_provider_e2e(
        repo,
        "codex",
        [str(fake)],
        "change VALUE to 2",
        allowed_files=["app.py"],
        tests=["python -c \"from pathlib import Path; assert 'VALUE = 2' in Path('app.py').read_text()\""],
        max_iterations=1,
    )

    assert result["status"] == "passed"
    assert result["execution"]["status"] == "passed"
    assert Path(result["evidence_file"]).is_file()
    assert target.read_text(encoding="utf-8") == "VALUE = 2\n"


def test_real_e2e_runner_never_counts_missing_provider_as_pass(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    missing = tmp_path / "codex"

    result = run_real_provider_e2e(repo, "codex", [str(missing)], "noop", max_iterations=1)

    assert result["status"] == "unavailable"
    assert result["reason"] == "provider_executable_unavailable"
    assert Path(result["evidence_file"]).is_file()


def test_real_e2e_matrix_is_incomplete_when_any_provider_is_unavailable(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    fake = _fake_codex(tmp_path / "codex")

    result = run_real_provider_matrix(
        repo,
        [
            {
                "provider": "codex",
                "argv": [str(fake)],
                "task": "change VALUE to 2",
                "allowed_files": ["app.py"],
                "tests": ["python -c \"from pathlib import Path; assert 'VALUE = 2' in Path('app.py').read_text()\""],
                "max_iterations": 1,
            },
            {
                "provider": "goose",
                "argv": [str(tmp_path / "goose")],
                "task": "noop",
                "max_iterations": 1,
            },
        ],
    )

    assert result["status"] == "incomplete"
    assert result["counts"]["passed"] == 1
    assert result["counts"]["unavailable"] == 1
