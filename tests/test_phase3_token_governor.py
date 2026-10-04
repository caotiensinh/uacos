from __future__ import annotations

from pathlib import Path

from uacos.execution.evidence_ledger import evidence_ledger_path
from uacos.orchestrator.contract import build_task_contract_v2
from uacos.token.governor import evaluate_token_budget, settle_token_usage, token_usage_summary


TASK = "task-token-1"
RUN = "run-token-1"


def _contract(max_tokens: int | None = 100):
    return build_task_contract_v2(
        "complete the task under a bounded token budget",
        allowed_files=["app.py"],
        required_tests=["unit"],
        required_evidence=["test_result"],
        max_tokens=max_tokens,
    )


def test_budget_allows_exact_limit_and_blocks_over_limit(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    contract = _contract(100)

    exact = evaluate_token_budget(
        repo, contract, task_id=TASK, run_id=RUN, requested_tokens=100, record_decision=False
    )
    over = evaluate_token_budget(
        repo, contract, task_id=TASK, run_id=RUN, requested_tokens=101, record_decision=False
    )

    assert exact["decision"] == "COMPACT"
    assert exact["projected_tokens"] == 100
    assert over["status"] == "blocked"
    assert over["decision"] == "STOP"
    assert over["reason"] == "contract_max_tokens_exceeded"


def test_near_limit_requests_compaction_before_exhaustion(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    result = evaluate_token_budget(
        repo, _contract(100), task_id=TASK, run_id=RUN, requested_tokens=80, record_decision=False
    )

    assert result["status"] == "ok"
    assert result["decision"] == "COMPACT"
    assert result["remaining_tokens"] == 20


def test_negative_usage_is_rejected_fail_closed(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    reserve = evaluate_token_budget(
        repo, _contract(), task_id=TASK, run_id=RUN, requested_tokens=-1, record_decision=False
    )
    settle = settle_token_usage(
        repo,
        _contract(),
        task_id=TASK,
        run_id=RUN,
        action_id="call-1",
        actual_tokens=-1,
    )

    assert reserve == {"status": "error", "decision": "STOP", "reason": "requested_tokens_must_be_nonnegative"}
    assert settle == {"status": "error", "decision": "STOP", "reason": "actual_tokens_must_be_nonnegative"}


def test_usage_is_exact_task_and_run_scoped(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    contract = _contract(100)

    settle_token_usage(repo, contract, task_id="other", run_id=RUN, action_id="x", actual_tokens=90)
    settle_token_usage(repo, contract, task_id=TASK, run_id="other-run", action_id="y", actual_tokens=90)
    settle_token_usage(repo, contract, task_id=TASK, run_id=RUN, action_id="z", actual_tokens=10)

    summary = token_usage_summary(repo, task_id=TASK, run_id=RUN)
    decision = evaluate_token_budget(
        repo, contract, task_id=TASK, run_id=RUN, requested_tokens=70, record_decision=False
    )

    assert summary["total_tokens"] == 10
    assert summary["settled_actions"] == 1
    assert decision["projected_tokens"] == 80
    assert decision["decision"] == "COMPACT"


def test_settlement_is_idempotent_per_action_id(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    contract = _contract(100)

    first = settle_token_usage(
        repo, contract, task_id=TASK, run_id=RUN, action_id="call-1", actual_tokens=25
    )
    second = settle_token_usage(
        repo, contract, task_id=TASK, run_id=RUN, action_id="call-1", actual_tokens=99
    )
    summary = token_usage_summary(repo, task_id=TASK, run_id=RUN)

    assert first["idempotent"] is False
    assert second["idempotent"] is True
    assert second["event_id"] == first["event_id"]
    assert second["actual_tokens"] == 25
    assert summary["total_tokens"] == 25
    assert summary["settled_actions"] == 1


def test_actual_usage_over_estimate_is_recorded_then_stops_future_calls(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    contract = _contract(100)

    reserve = evaluate_token_budget(
        repo,
        contract,
        task_id=TASK,
        run_id=RUN,
        action_id="call-1",
        requested_tokens=60,
        record_decision=False,
    )
    settled = settle_token_usage(
        repo,
        contract,
        task_id=TASK,
        run_id=RUN,
        action_id="call-1",
        actual_tokens=110,
        input_tokens=70,
        output_tokens=40,
        provider="test-provider",
        model="test-model",
    )
    next_call = evaluate_token_budget(
        repo,
        contract,
        task_id=TASK,
        run_id=RUN,
        action_id="call-2",
        requested_tokens=1,
        record_decision=False,
    )

    assert reserve["decision"] == "ALLOW"
    assert settled["decision"] == "STOP"
    assert settled["reason"] == "actual_usage_exceeded_contract_budget"
    assert settled["consumed_tokens"] == 110
    assert next_call["decision"] == "STOP"
    assert next_call["consumed_tokens"] == 110


def test_tampered_ledger_blocks_budget_decision_and_settlement(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    contract = _contract(100)
    settle_token_usage(repo, contract, task_id=TASK, run_id=RUN, action_id="call-1", actual_tokens=10)

    path = evidence_ledger_path(repo)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"total_tokens":10', '"total_tokens":11', 1), encoding="utf-8")

    decision = evaluate_token_budget(
        repo, contract, task_id=TASK, run_id=RUN, requested_tokens=1, record_decision=False
    )
    settled = settle_token_usage(
        repo, contract, task_id=TASK, run_id=RUN, action_id="call-2", actual_tokens=1
    )

    assert decision["decision"] == "STOP"
    assert decision["reason"] == "evidence_ledger_invalid"
    assert settled["decision"] == "STOP"
    assert settled["reason"] == "evidence_ledger_invalid"
