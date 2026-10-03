import json
from pathlib import Path

from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.execution.evidence_ledger import (
    append_evidence_event,
    evidence_ledger_path,
    read_evidence_ledger,
    verify_evidence_ledger,
)
from uacos.security.evidence_gate import evaluate_mutation_evidence_gate


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
"""


class PatchAdapter:
    name = "fixture"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def run(self, request):
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            patch=PATCH,
            output=PATCH,
        )


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    return repo, target


def test_enabled_gate_blocks_missing_evidence_before_source_mutation(tmp_path: Path):
    repo, target = _repo(tmp_path)

    result = run_safe_agent_execution(
        repo,
        "change app value",
        PatchAdapter(),
        allowed_files=["app.py"],
        max_iterations=1,
        mutation_evidence_contract={
            "enabled": True,
            "required_event_ids": ["EV-missing"],
            "required_event_types": ["reproduction"],
        },
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "mutation_evidence_gate_blocked"
    assert result["evidence_gate"]["decision"] == "deny"
    assert "required_evidence_missing" in result["evidence_gate"]["findings"]
    assert result["preconditions"] is None
    assert result["patch_apply"] is None
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"
    rows = read_evidence_ledger(repo)
    assert rows[-1]["event_type"] == "mutation_gate"
    assert rows[-1]["status"] == "blocked"
    assert verify_evidence_ledger(repo)["status"] == "pass"


def test_verified_evidence_allows_existing_safe_execution_pipeline(tmp_path: Path):
    repo, target = _repo(tmp_path)
    evidence = append_evidence_event(
        repo,
        event_type="reproduction",
        source="phase3-test",
        status="verified",
        task_id="TASK-1",
        data={"failure_reproduced": True},
    )

    result = run_safe_agent_execution(
        repo,
        "change app value",
        PatchAdapter(),
        allowed_files=["app.py"],
        tests=["python -c \"from pathlib import Path; assert 'VALUE = 2' in Path('app.py').read_text()\""],
        max_iterations=1,
        mutation_evidence_contract={
            "enabled": True,
            "task_id": "TASK-1",
            "required_event_ids": [evidence["event_id"]],
            "required_event_types": ["reproduction"],
        },
    )

    assert result["evidence_gate"]["status"] == "pass"
    assert result["evidence_gate"]["decision"] == "allow"
    assert result["evidence_gate"]["decision_event_id"]
    assert result["status"] == "passed"
    assert result["reason"] == "patch_applied_tests_passed"
    assert result["patch_apply"]["status"] == "applied"
    assert target.read_text(encoding="utf-8") == "VALUE = 2\n"
    assert verify_evidence_ledger(repo)["status"] == "pass"


def test_negative_evidence_blocks_even_when_event_exists(tmp_path: Path):
    repo, target = _repo(tmp_path)
    evidence = append_evidence_event(
        repo,
        event_type="reproduction",
        source="phase3-test",
        status="failed",
        task_id="TASK-2",
    )

    result = run_safe_agent_execution(
        repo,
        "change app value",
        PatchAdapter(),
        allowed_files=["app.py"],
        max_iterations=1,
        mutation_evidence_contract={
            "enabled": True,
            "task_id": "TASK-2",
            "required_event_ids": [evidence["event_id"]],
            "required_event_types": ["reproduction"],
        },
    )

    assert result["status"] == "blocked"
    assert "negative_evidence_present" in result["evidence_gate"]["findings"]
    assert result["patch_apply"] is None
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"


def test_enabled_gate_requires_declared_mutation_scope(tmp_path: Path):
    repo, target = _repo(tmp_path)
    evidence = append_evidence_event(repo, event_type="context_ready", source="phase3-test", status="ready")

    gate = evaluate_mutation_evidence_gate(
        repo,
        patch_text=PATCH,
        allowed_files=[],
        allowed_dirs=[],
        contract={
            "enabled": True,
            "required_event_ids": [evidence["event_id"]],
            "required_event_types": ["context_ready"],
        },
        run_id="RUN-SCOPE",
    )

    assert gate["decision"] == "deny"
    assert "mutation_scope_missing" in gate["findings"]
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"


def test_tampered_ledger_blocks_gate_without_appending_decision(tmp_path: Path):
    repo, target = _repo(tmp_path)
    evidence = append_evidence_event(repo, event_type="reproduction", source="phase3-test", status="verified")
    path = evidence_ledger_path(repo)
    row = json.loads(path.read_text(encoding="utf-8"))
    row["status"] = "failed"
    tampered = json.dumps(row) + "\n"
    path.write_text(tampered, encoding="utf-8")

    gate = evaluate_mutation_evidence_gate(
        repo,
        patch_text=PATCH,
        allowed_files=["app.py"],
        allowed_dirs=[],
        contract={
            "enabled": True,
            "required_event_ids": [evidence["event_id"]],
            "required_event_types": ["reproduction"],
        },
        run_id="RUN-TAMPER",
    )

    assert gate["decision"] == "deny"
    assert gate["reason"] == "evidence_ledger_invalid"
    assert gate["decision_event_id"] is None
    assert path.read_text(encoding="utf-8") == tampered
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"


def test_task_mismatched_evidence_is_rejected(tmp_path: Path):
    repo, target = _repo(tmp_path)
    evidence = append_evidence_event(
        repo,
        event_type="reproduction",
        source="phase3-test",
        status="verified",
        task_id="OTHER-TASK",
    )

    gate = evaluate_mutation_evidence_gate(
        repo,
        patch_text=PATCH,
        allowed_files=["app.py"],
        allowed_dirs=[],
        contract={
            "enabled": True,
            "task_id": "TASK-EXPECTED",
            "required_event_ids": [evidence["event_id"]],
            "required_event_types": ["reproduction"],
        },
    )

    assert gate["decision"] == "deny"
    assert "evidence_task_mismatch" in gate["findings"]
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"
