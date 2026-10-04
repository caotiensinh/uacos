from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import uacos.runtime.evidence_guided_recovery as recovery
from uacos.execution.evidence_ledger import (
    append_evidence_event,
    evidence_ledger_path,
    read_evidence_ledger,
)


def _failed_after_tests(run_id: str = "run-1", *, rolled_back: bool = True) -> dict:
    return {
        "status": "failed",
        "reason": "tests_failed",
        "run_id": run_id,
        "patch_apply": {"status": "applied"},
        "rollback": {"status": "rolled_back" if rolled_back else "rollback_failed"},
    }


def test_verified_rollback_allows_one_bounded_repair_and_persists_event(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    decision = recovery.record_recovery_decision(
        repo,
        _failed_after_tests(),
        task_id="task-1",
        repair_attempts=0,
        max_repair_attempts=1,
    )

    assert decision["action"] == "REPAIR"
    assert decision["strategy"] == "REPLAN_FROM_TEST_EVIDENCE"
    assert decision["persisted"] is True
    rows = read_evidence_ledger(repo)
    assert len(rows) == 1
    assert rows[0]["event_type"] == "recovery_decision"
    assert rows[0]["task_id"] == "task-1"
    assert rows[0]["run_id"] == "run-1"
    assert rows[0]["data"]["rollback_verified"] is True
    assert rows[0]["data"]["real_failure_observed"] is True


def test_mutated_failure_without_verified_rollback_stops(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    decision = recovery.record_recovery_decision(
        repo,
        _failed_after_tests(rolled_back=False),
        task_id="task-1",
    )

    assert decision["action"] == "STOP"
    assert decision["reason"] == "verified_rollback_required_before_repair"


def test_repeated_failure_stops_instead_of_repair_loop(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    decision = recovery.record_recovery_decision(
        repo,
        _failed_after_tests(),
        task_id="task-1",
        repeated_failure=True,
    )

    assert decision["action"] == "STOP"
    assert decision["reason"] == "repeated_failure_signature"


def test_recovery_decision_is_idempotent_for_same_run_attempt(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _failed_after_tests()

    first = recovery.record_recovery_decision(repo, result, task_id="task-1")
    second = recovery.record_recovery_decision(repo, result, task_id="task-1")

    assert first["evidence_event_id"] == second["evidence_event_id"]
    assert first["idempotent_replay"] is False
    assert second["idempotent_replay"] is True
    assert len(read_evidence_ledger(repo)) == 1


def test_concurrent_recovery_decisions_append_exactly_once(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _failed_after_tests("run-concurrent")

    def decide():
        return recovery.record_recovery_decision(repo, result, task_id="task-concurrent")

    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = list(pool.map(lambda _: decide(), range(2)))

    event_ids = {row["evidence_event_id"] for row in decisions}
    assert len(event_ids) == 1
    assert all(row["action"] == "REPAIR" for row in decisions)
    assert len(read_evidence_ledger(repo)) == 1
    assert sorted(row["idempotent_replay"] for row in decisions) == [False, True]


def test_recovery_action_conflict_fails_closed(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    recovery.record_recovery_decision(repo, _failed_after_tests(), task_id="task-1")
    changed = _failed_after_tests()
    changed["reason"] = "tests_timed_out"
    conflict = recovery.record_recovery_decision(repo, changed, task_id="task-1")

    assert conflict["action"] == "STOP"
    assert conflict["reason"] == "recovery_action_id_conflict"
    assert conflict["persisted"] is False
    assert len(read_evidence_ledger(repo)) == 1


def test_recovery_replay_requires_same_rollback_and_control_inputs(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    recovery.record_recovery_decision(
        repo,
        _failed_after_tests(rolled_back=True),
        task_id="task-1",
        repair_attempts=0,
        max_repair_attempts=1,
        repeated_failure=False,
    )

    rollback_changed = recovery.record_recovery_decision(
        repo,
        _failed_after_tests(rolled_back=False),
        task_id="task-1",
        repair_attempts=0,
        max_repair_attempts=1,
        repeated_failure=False,
    )
    assert rollback_changed["action"] == "STOP"
    assert rollback_changed["reason"] == "recovery_action_id_conflict"

    repeated_changed = recovery.record_recovery_decision(
        repo,
        _failed_after_tests(rolled_back=True),
        task_id="task-1",
        repair_attempts=0,
        max_repair_attempts=1,
        repeated_failure=True,
    )
    assert repeated_changed["action"] == "STOP"
    assert repeated_changed["reason"] == "recovery_action_id_conflict"
    assert len(read_evidence_ledger(repo)) == 1


def test_task_id_is_part_of_recovery_identity_when_run_is_unbound(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    first = _failed_after_tests("")
    second = _failed_after_tests("")

    one = recovery.record_recovery_decision(repo, first, task_id="task-a")
    two = recovery.record_recovery_decision(repo, second, task_id="task-b")

    assert one["action"] == "REPAIR"
    assert two["action"] == "REPAIR"
    assert one["evidence_event_id"] != two["evidence_event_id"]
    assert len(read_evidence_ledger(repo)) == 2


def test_tampered_ledger_blocks_recovery_decision_without_append(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    append_evidence_event(
        repo,
        event_type="test_result",
        source="fixture",
        status="fail",
        task_id="task-1",
        run_id="run-1",
    )
    path = evidence_ledger_path(repo)
    path.write_text(path.read_text(encoding="utf-8").replace('"status":"fail"', '"status":"pass"'), encoding="utf-8")
    before = path.read_text(encoding="utf-8")

    decision = recovery.record_recovery_decision(repo, _failed_after_tests(), task_id="task-1")

    assert decision["action"] == "STOP"
    assert decision["reason"] == "evidence_ledger_invalid"
    assert decision["persisted"] is False
    assert path.read_text(encoding="utf-8") == before


def test_wrapper_observes_once_and_never_auto_retries(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    calls = []

    def fake_safe_execution(repo_root, task, adapter, **kwargs):
        calls.append((repo_root, task, adapter, kwargs))
        return _failed_after_tests("run-wrap")

    monkeypatch.setattr(recovery, "run_safe_agent_execution", fake_safe_execution)
    result = recovery.run_safe_execution_with_recovery(
        repo,
        "fix task",
        object(),
        task_id="task-wrap",
        max_repair_attempts=1,
    )

    assert len(calls) == 1
    assert result["status"] == "failed"
    assert result["recovery_decision"]["action"] == "REPAIR"
    assert len(read_evidence_ledger(repo)) == 1


def test_success_does_not_create_recovery_event(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()

    monkeypatch.setattr(
        recovery,
        "run_safe_agent_execution",
        lambda repo_root, task, adapter, **kwargs: {
            "status": "passed",
            "reason": "patch_applied_tests_passed",
            "run_id": "run-ok",
        },
    )
    result = recovery.run_safe_execution_with_recovery(repo, "ok task", object(), task_id="task-ok")

    assert result["recovery_decision"] is None
    assert read_evidence_ledger(repo) == []
