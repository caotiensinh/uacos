from pathlib import Path

from uacos.execution.evidence_ledger import append_evidence_event, evidence_ledger_path, read_evidence_ledger
from uacos.orchestrator.contract import build_task_contract_v2
from uacos.validation.outcome_verifier import verify_task_outcome


TASK = "task-outcome-1"


def _contract():
    return build_task_contract_v2(
        "make the user-visible flow work",
        allowed_files=["app.py"],
        required_tests=["unit:user-flow"],
        runtime_checks=["service:health"],
        outcome_checks=["user:visible-result"],
        required_evidence=[
            "patch_apply",
            "unit:user-flow",
            "service:health",
            "user:visible-result",
            "result_recorded",
        ],
    )


def _event(repo: Path, event_type: str, status: str = "pass", *, task_id: str = TASK, check_id: str | None = None, diff_hash: str | None = None):
    data = {"check_id": check_id} if check_id else {}
    return append_evidence_event(
        repo,
        event_type=event_type,
        source="test.host",
        status=status,
        task_id=task_id,
        diff_hash=diff_hash,
        data=data,
    )


def test_tests_pass_but_runtime_and_user_outcome_missing_is_overall_fail(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _event(repo, "patch_apply", diff_hash="d" * 64)
    _event(repo, "test_result", check_id="unit:user-flow")
    _event(repo, "result_recorded")

    verdict = verify_task_outcome(repo, _contract(), task_id=TASK, record_verdict=False)

    assert verdict["overall"] == "FAIL"
    assert verdict["layers"]["CODE_VALID"]["state"] == "PASS"
    assert verdict["layers"]["TEST_VALID"]["state"] == "PASS"
    assert verdict["layers"]["SYSTEM_VALID"]["state"] == "FAIL"
    assert verdict["layers"]["USER_OUTCOME_VALID"]["state"] == "FAIL"
    assert verdict["done_predicate"]["state"] == "not_done"


def test_full_layered_evidence_passes_and_records_verdict(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    patch = _event(repo, "patch_apply", diff_hash="a" * 64)
    test = _event(repo, "test_result", check_id="unit:user-flow")
    runtime = _event(repo, "runtime_check", check_id="service:health")
    outcome = _event(repo, "outcome_check", check_id="user:visible-result")
    _event(repo, "result_recorded")

    verdict = verify_task_outcome(repo, _contract(), task_id=TASK)

    assert verdict["status"] == "pass"
    assert verdict["overall"] == "PASS"
    assert verdict["done_predicate"]["state"] == "done"
    assert {name: row["state"] for name, row in verdict["layers"].items()} == {
        "CODE_VALID": "PASS",
        "TEST_VALID": "PASS",
        "SYSTEM_VALID": "PASS",
        "USER_OUTCOME_VALID": "PASS",
    }
    assert set(verdict["evidence_refs"]) == {patch["event_id"], test["event_id"], runtime["event_id"], outcome["event_id"]}
    rows = read_evidence_ledger(repo)
    assert rows[-1]["event_id"] == verdict["verdict_event_id"]
    assert rows[-1]["event_type"] == "outcome_verdict"
    assert rows[-1]["status"] == "pass"


def test_mutation_gate_allow_does_not_count_as_code_changed(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _event(repo, "mutation_gate", status="allow")
    _event(repo, "test_result", check_id="unit:user-flow")
    _event(repo, "runtime_check", check_id="service:health")
    _event(repo, "outcome_check", check_id="user:visible-result")
    _event(repo, "result_recorded")

    verdict = verify_task_outcome(repo, _contract(), task_id=TASK, record_verdict=False)

    assert verdict["overall"] == "FAIL"
    assert verdict["layers"]["CODE_VALID"] == {
        "state": "FAIL",
        "reason": "applied_diff_evidence_missing",
    }


def test_negative_runtime_evidence_overrides_test_success(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _event(repo, "patch_apply", diff_hash="b" * 64)
    _event(repo, "test_result", check_id="unit:user-flow")
    _event(repo, "runtime_check", status="fail", check_id="service:health")
    _event(repo, "outcome_check", check_id="user:visible-result")
    _event(repo, "result_recorded")

    verdict = verify_task_outcome(repo, _contract(), task_id=TASK, record_verdict=False)

    assert verdict["overall"] == "FAIL"
    assert verdict["layers"]["TEST_VALID"]["state"] == "PASS"
    assert verdict["layers"]["SYSTEM_VALID"]["state"] == "FAIL"
    assert verdict["layers"]["SYSTEM_VALID"]["reason"] == "contradictory_evidence"
    assert verdict["layers"]["SYSTEM_VALID"]["contradictions"] == ["service:health"]


def test_cross_task_and_unbound_evidence_cannot_satisfy_task(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _event(repo, "patch_apply", task_id="other-task", diff_hash="c" * 64)
    _event(repo, "test_result", task_id="other-task", check_id="unit:user-flow")
    _event(repo, "runtime_check", task_id="other-task", check_id="service:health")
    _event(repo, "outcome_check", task_id="other-task", check_id="user:visible-result")
    _event(repo, "result_recorded", task_id="other-task")
    append_evidence_event(
        repo,
        event_type="runtime_check",
        source="test.host",
        status="pass",
        task_id=None,
        data={"check_id": "service:health"},
    )

    verdict = verify_task_outcome(repo, _contract(), task_id=TASK, record_verdict=False)

    assert verdict["overall"] == "FAIL"
    assert verdict["layers"]["CODE_VALID"]["state"] == "FAIL"
    assert verdict["layers"]["TEST_VALID"]["state"] == "FAIL"
    assert verdict["layers"]["SYSTEM_VALID"]["state"] == "FAIL"
    assert verdict["layers"]["USER_OUTCOME_VALID"]["state"] == "FAIL"


def test_tampered_ledger_fails_closed_and_does_not_append_verdict(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _event(repo, "patch_apply", diff_hash="e" * 64)
    before = read_evidence_ledger(repo)
    path = evidence_ledger_path(repo)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"status":"pass"', '"status":"fail"', 1), encoding="utf-8")

    verdict = verify_task_outcome(repo, _contract(), task_id=TASK)

    assert verdict["status"] == "fail"
    assert verdict["overall"] == "FAIL"
    assert verdict["reason"] == "evidence_ledger_invalid"
    assert len(path.read_text(encoding="utf-8").splitlines()) == len(before)
