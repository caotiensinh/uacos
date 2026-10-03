from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from uacos.runtime.run_state import (
    begin_iteration,
    create_run_state,
    enforce_runtime_conditions,
    load_run_state,
    request_cancel,
    transition_run,
)


def test_run_state_persists_transitions_and_idempotency(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    created = create_run_state(repo, "fix app:value", run_id="RUN-fixed", max_iterations=2)
    assert created["status"] == "queued"

    first = begin_iteration(repo, "RUN-fixed", idempotency_key="iteration-1")
    assert first["status"] == "running"
    assert first["iteration"] == 1

    replay = begin_iteration(repo, "RUN-fixed", idempotency_key="iteration-1")
    assert replay["idempotent_replay"] is True
    assert replay["iteration"] == 1

    validating = transition_run(
        repo,
        "RUN-fixed",
        "validating",
        reason="patch_received",
        evidence={"patch_sha": "abc"},
        idempotency_key="validate-1",
    )
    assert validating["status"] == "validating"
    assert validating["events"][-1]["evidence"]["patch_sha"] == "abc"

    persisted = load_run_state(repo, "RUN-fixed")
    assert persisted["status"] == "validating"
    assert persisted["iteration"] == 1


def test_run_state_rejects_illegal_transition(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    state = create_run_state(repo, "task")

    with pytest.raises(ValueError, match="invalid_transition:queued->passed"):
        transition_run(repo, state["run_id"], "passed", reason="cannot_skip")


def test_cancel_request_is_durable_and_enforced(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    state = create_run_state(repo, "task")
    run_id = state["run_id"]
    begin_iteration(repo, run_id)

    requested = request_cancel(repo, run_id)
    assert requested["cancel_requested"] is True
    cancelled = enforce_runtime_conditions(repo, run_id)
    assert cancelled["status"] == "cancelled"
    assert load_run_state(repo, run_id)["status"] == "cancelled"


def test_deadline_transitions_run_to_timed_out(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    state = create_run_state(repo, "task", deadline_seconds=60)
    run_id = state["run_id"]
    begin_iteration(repo, run_id)

    future = datetime.now(timezone.utc) + timedelta(minutes=2)
    timed_out = enforce_runtime_conditions(repo, run_id, now=future)
    assert timed_out["status"] == "timed_out"
    assert timed_out["events"][-1]["reason"] == "deadline_exceeded"


def test_iteration_budget_fails_closed(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    state = create_run_state(repo, "task", max_iterations=1)
    run_id = state["run_id"]
    first = begin_iteration(repo, run_id)
    assert first["iteration"] == 1

    retry = transition_run(repo, run_id, "retrying", reason="tests_failed")
    assert retry["status"] == "retrying"
    exhausted = begin_iteration(repo, run_id, idempotency_key="iteration-2")
    assert exhausted["status"] == "failed"
    assert exhausted["events"][-1]["reason"] == "max_iterations_exhausted"
