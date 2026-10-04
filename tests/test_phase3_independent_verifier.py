from __future__ import annotations

from pathlib import Path

from uacos.execution.evidence_ledger import (
    append_evidence_event,
    evidence_ledger_path,
    read_evidence_ledger,
)
from uacos.orchestrator.contract import build_task_contract_v2
from uacos.validation.independent_verifier import verify_independently
from uacos.validation.outcome_verifier import verify_task_outcome

TASK = "task-independent-1"
RUN = "run-independent-1"
ACTOR = "agent:coder"
VERIFIER = "verifier:deterministic"


def _contract():
    return build_task_contract_v2(
        "make the real user flow work",
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


def _event(
    repo: Path,
    event_type: str,
    *,
    status: str = "pass",
    task_id: str = TASK,
    run_id: str = RUN,
    check_id: str | None = None,
    diff_hash: str | None = None,
    source: str = "test.host",
):
    return append_evidence_event(
        repo,
        event_type=event_type,
        source=source,
        status=status,
        task_id=task_id,
        run_id=run_id,
        diff_hash=diff_hash,
        data={"check_id": check_id} if check_id else {},
    )


def _full_evidence(repo: Path, *, task_id: str = TASK, run_id: str = RUN):
    patch = _event(repo, "patch_apply", task_id=task_id, run_id=run_id, diff_hash="a" * 64)
    test = _event(repo, "test_result", task_id=task_id, run_id=run_id, check_id="unit:user-flow")
    runtime = _event(repo, "runtime_check", task_id=task_id, run_id=run_id, check_id="service:health")
    outcome = _event(repo, "outcome_check", task_id=task_id, run_id=run_id, check_id="user:visible-result")
    _event(repo, "result_recorded", task_id=task_id, run_id=run_id)
    return {patch["event_id"], test["event_id"], runtime["event_id"], outcome["event_id"]}


def test_independent_verifier_passes_only_from_exact_canonical_evidence(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    refs = _full_evidence(repo)

    verdict = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-1",
    )

    assert verdict["status"] == "pass"
    assert verdict["overall"] == "PASS"
    assert verdict["actor_id"] == ACTOR
    assert verdict["verifier_id"] == VERIFIER
    assert set(verdict["evidence_refs"]) == refs
    row = read_evidence_ledger(repo)[-1]
    assert row["event_type"] == "independent_verification"
    assert row["source"] == "uacos.validation.independent_verifier"
    assert row["task_id"] == TASK
    assert row["run_id"] == RUN
    assert row["action_id"] == "verify-1"
    assert row["data"]["actor_id"] == ACTOR
    assert row["data"]["verifier_id"] == VERIFIER
    assert row["data"]["contract_id"] == _contract()["contract_id"]


def test_self_verification_is_forbidden_and_records_nothing(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _full_evidence(repo)
    before = len(read_evidence_ledger(repo))

    verdict = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=ACTOR,
        verification_id="verify-self",
    )

    assert verdict["overall"] == "FAIL"
    assert verdict["reason"] == "self_verification_forbidden"
    assert len(read_evidence_ledger(repo)) == before


def test_agent_success_prose_cannot_replace_missing_runtime_or_outcome_evidence(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _event(repo, "patch_apply", diff_hash="b" * 64)
    _event(repo, "test_result", check_id="unit:user-flow")
    _event(repo, "result_recorded")
    _event(repo, "agent_claim", status="pass", source="agent:coder")
    _event(repo, "final_result", status="pass", source="agent:coder")

    verdict = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-prose",
        record_verdict=False,
    )

    assert verdict["overall"] == "FAIL"
    assert verdict["outcome"]["layers"]["SYSTEM_VALID"]["state"] == "FAIL"
    assert verdict["outcome"]["layers"]["USER_OUTCOME_VALID"]["state"] == "FAIL"


def test_previous_run_evidence_cannot_make_new_run_pass(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _full_evidence(repo, run_id="old-run")

    old_verdict = verify_task_outcome(
        repo, _contract(), task_id=TASK, run_id="old-run", record_verdict=False
    )
    new_verdict = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-new-run",
        record_verdict=False,
    )

    assert old_verdict["overall"] == "PASS"
    assert new_verdict["overall"] == "FAIL"
    assert new_verdict["outcome"]["run_id"] == RUN
    assert new_verdict["outcome"]["layers"]["TEST_VALID"]["state"] == "FAIL"


def test_cross_task_evidence_cannot_satisfy_independent_verifier(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _full_evidence(repo, task_id="other-task")

    verdict = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-cross-task",
        record_verdict=False,
    )

    assert verdict["overall"] == "FAIL"
    assert verdict["outcome"]["layers"]["CODE_VALID"]["state"] == "FAIL"


def test_tampered_ledger_fails_closed_before_independent_verdict(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _full_evidence(repo)
    path = evidence_ledger_path(repo)
    path.write_text(
        path.read_text(encoding="utf-8").replace('"status":"pass"', '"status":"fail"', 1),
        encoding="utf-8",
    )
    before = len(path.read_text(encoding="utf-8").splitlines())

    verdict = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-tamper",
    )

    assert verdict["overall"] == "FAIL"
    assert verdict["reason"] == "evidence_ledger_invalid"
    assert len(path.read_text(encoding="utf-8").splitlines()) == before


def test_verification_id_is_idempotent_but_identity_conflicts_fail(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _full_evidence(repo)
    contract = _contract()

    first = verify_independently(
        repo,
        contract,
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-idempotent",
    )
    second = verify_independently(
        repo,
        contract,
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id=VERIFIER,
        verification_id="verify-idempotent",
    )
    conflict = verify_independently(
        repo,
        contract,
        task_id=TASK,
        run_id=RUN,
        actor_id="agent:other",
        verifier_id=VERIFIER,
        verification_id="verify-idempotent",
    )

    assert first["idempotent"] is False
    assert second["idempotent"] is True
    assert second["verification_event_id"] == first["verification_event_id"]
    assert conflict["overall"] == "FAIL"
    assert conflict["reason"] == "verification_id_conflict"
    rows = [row for row in read_evidence_ledger(repo) if row["event_type"] == "independent_verification"]
    assert len(rows) == 1


def test_missing_actor_or_verifier_identity_fails_closed(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _full_evidence(repo)

    no_actor = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id="",
        verifier_id=VERIFIER,
        verification_id="verify-no-actor",
    )
    no_verifier = verify_independently(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        actor_id=ACTOR,
        verifier_id="",
        verification_id="verify-no-verifier",
    )

    assert no_actor["reason"] == "actor_id_required"
    assert no_verifier["reason"] == "verifier_id_required"
