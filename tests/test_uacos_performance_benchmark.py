import json
import subprocess
import sys
from pathlib import Path


def test_uacos_performance_benchmark_runs_on_repo():
    root = Path(__file__).resolve().parents[1]
    report = root / "reports" / "test_uacos_performance_report.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/uacos_performance_benchmark.py",
            "--repo",
            ".",
            "--task",
            "fix MCP SSE endpoint and docs cleanup",
            "--max-files",
            "4",
            "--max-tokens",
            "4000",
            "--report",
            str(report),
        ],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["status"] == "pass"
    assert data["summary"]["baseline_without_uacos_tokens_est"] >= data["summary"]["uacos_context_tokens_est"]
    assert data["summary"]["tokens_saved_est"] >= 0
    assert data["tasks"][0]["selected_file_count"] > 0
