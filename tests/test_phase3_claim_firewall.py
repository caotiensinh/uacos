import json
from pathlib import Path

from uacos.agent.task import create_task
from uacos.execution.artifacts import evidence_report_v2
from uacos.execution.evidence_ledger import (
    append_evidence_event,
    evidence_ledger_path,
    read_evidence_ledger,
)
from uacos.storage import init_storage
from uacos.validation.claim_firewall import (
    CONTRADICTED,
    PARTIAL,
    SUPPORTED,
    UNSUPPORTED,
    evaluate_and_record_claim,
    evaluate_claim,
    evaluate_claims,
    factual_claims_only,
)


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)
    return repo


def test_tests_passed_claim_requires_exact_host_evidence(tmp_path: Path):
    repo = _repo(tmp_path)
    first = append_evidence_event(
        repo,
        event_type="test_command",
        source="test_runner",
        status="pass",
        command="pytest -q tests/test_api.py",
        exit_code=0,
    )
    second = append_evidence_event(
        repo,
        event_type="test_command",
        source="test_runner",
        status="pass",
        command="python scripts/self_check.py",
        exit_code=0,
    )

    result = evaluate_claim(
        repo,
        {
            "claim_id": "C1",
            "claim_type": "tests_passed",
            "text": "Required tests passed",
            "evidence_event_ids": [first["event_id"], second["event_id"]],
            "requirements": {
                "required_event_types": ["test_command"],
                "accepted_statuses": ["pass"],
                "min_events": 2,
                "all_relevant_must_be_accepted": True,
                "expected_commands": ["pytest -q tests/test_api.py", "python scripts/self_check.py"],
            },
        },
    )

    assert result["status"] == SUPPORTED
    assert result["reason"] == "evidence_policy_satisfied"
    assert result["missing_commands"] == []


def test_claim_is_contradicted_by_referenced_failed_or_blocked_evidence(tmp_path: Path):
    repo = _repo(tmp_path)
    passed = append_evidence_event(repo, event_type="test_command", source="test_runner", status="pass", command="pytest -q")
    blocked = append_evidence_event(repo, event_type="test_command", source="test_runner", status="blocked", command="rm -rf /")

    result = evaluate_claim(
        repo,
        {
            "claim_id": "C2",
            "claim_type": "tests_passed",
            "text": "All referenced tests passed",
            "evidence_event_ids": [passed["event_id"], blocked["event_id"]],
        },
    )

    assert result["status"] == CONTRADICTED
    assert result["contradicting_event_ids"] == [blocked["event_id"]]


def test_missing_or_unknown_evidence_never_becomes_supported(tmp_path: Path):
    repo = _repo(tmp_path)

    no_evidence = evaluate_claim(
        repo,
        {"claim_id": "C3", "claim_type": "tests_passed", "text": "Tests passed", "evidence_event_ids": []},
    )
    missing = evaluate_claim(
        repo,
        {"claim_id": "C4", "claim_type": "tests_passed", "text": "Tests passed", "evidence_event_ids": ["EV-missing"]},
    )

    assert no_evidence["status"] == UNSUPPORTED
    assert no_evidence["reason"] == "evidence_required"
    assert missing["status"] == UNSUPPORTED
    assert missing["reason"] == "no_relevant_evidence"


def test_expected_command_gap_is_partial_not_pass(tmp_path: Path):
    repo = _repo(tmp_path)
    event = append_evidence_event(repo, event_type="test_command", source="test_runner", status="pass", command="pytest -q")

    result = evaluate_claim(
        repo,
        {
            "claim_id": "C5",
            "claim_type": "tests_passed",
            "text": "Required verification passed",
            "evidence_event_ids": [event["event_id"]],
            "requirements": {
                "required_event_types": ["test_command"],
                "accepted_statuses": ["pass"],
                "min_events": 1,
                "expected_commands": ["pytest -q", "python scripts/self_check.py"],
            },
        },
    )

    assert result["status"] == PARTIAL
    assert result["missing_commands"] == ["python scripts/self_check.py"]


def test_patch_claim_requires_valid_artifact_and_real_diff_hash(tmp_path: Path):
    repo = _repo(tmp_path)
    without_diff = append_evidence_event(repo, event_type="agent_artifact", source="artifacts", status="pass")
    with_diff = append_evidence_event(repo, event_type="agent_artifact", source="artifacts", status="pass", diff_hash="abc123")

    partial = evaluate_claim(
        repo,
        {"claim_id": "C6", "claim_type": "patch_validated", "text": "Patch validated", "evidence_event_ids": [without_diff["event_id"]]},
    )
    supported = evaluate_claim(
        repo,
        {"claim_id": "C7", "claim_type": "patch_validated", "text": "Patch validated", "evidence_event_ids": [with_diff["event_id"]]},
    )

    assert partial["status"] == PARTIAL
    assert partial["events_missing_required_fields"] == [without_diff["event_id"]]
    assert supported["status"] == SUPPORTED


def test_tampered_ledger_fails_claim_closed(tmp_path: Path):
    repo = _repo(tmp_path)
    event = append_evidence_event(repo, event_type="test_command", source="test_runner", status="pass", command="pytest -q")
    path = evidence_ledger_path(repo)
    row = json.loads(path.read_text(encoding="utf-8"))
    row["status"] = "recorded"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    result = evaluate_claim(
        repo,
        {"claim_id": "C8", "claim_type": "tests_passed", "text": "Tests passed", "evidence_event_ids": [event["event_id"]]},
    )

    assert result["status"] == UNSUPPORTED
    assert result["reason"] == "evidence_ledger_invalid"


def test_tampered_ledger_never_receives_new_claim_decision(tmp_path: Path):
    repo = _repo(tmp_path)
    event = append_evidence_event(repo, event_type="test_command", source="test_runner", status="pass", command="pytest -q")
    path = evidence_ledger_path(repo)
    row = json.loads(path.read_text(encoding="utf-8"))
    row["status"] = "recorded"
    tampered = json.dumps(row) + "\n"
    path.write_text(tampered, encoding="utf-8")

    result = evaluate_and_record_claim(
        repo,
        {"claim_id": "C8B", "claim_type": "tests_passed", "text": "Tests passed", "evidence_event_ids": [event["event_id"]]},
    )

    assert result["status"] == UNSUPPORTED
    assert result["reason"] == "evidence_ledger_invalid"
    assert result["decision_recorded"] is False
    assert result["decision_event_id"] is None
    assert path.read_text(encoding="utf-8") == tampered


def test_batch_firewall_blocks_report_and_only_exposes_supported_facts(tmp_path: Path):
    repo = _repo(tmp_path)
    event = append_evidence_event(repo, event_type="test_command", source="test_runner", status="pass", command="pytest -q")
    report = evaluate_claims(
        repo,
        [
            {"claim_id": "GOOD", "claim_type": "tests_passed", "text": "Tests passed", "evidence_event_ids": [event["event_id"]]},
            {"claim_id": "BAD", "claim_type": "tests_passed", "text": "Everything passed", "evidence_event_ids": []},
        ],
    )

    assert report["status"] == "blocked"
    assert report["unsupported_claim_ids"] == ["BAD"]
    assert [claim["claim_id"] for claim in factual_claims_only(report)] == ["GOOD"]


def test_evidence_report_only_promotes_supported_claims_to_verified_facts(tmp_path: Path):
    repo = _repo(tmp_path)
    task_file = create_task(repo, "Evidence report", "Render only verified claims", allowed_files=["app.py"])
    event = append_evidence_event(repo, event_type="test_command", source="test_runner", status="pass", command="pytest -q")
    claim_report = evaluate_claims(
        repo,
        [
            {"claim_id": "GOOD", "claim_type": "tests_passed", "text": "Tests passed", "evidence_event_ids": [event["event_id"]]},
            {"claim_id": "BAD", "claim_type": "tests_passed", "text": "Everything passed", "evidence_event_ids": []},
        ],
    )

    report = evidence_report_v2(repo, task_file, claim_report=claim_report)

    assert "VERIFIED `GOOD` / `tests_passed`" in report
    assert "VERIFIED `BAD`" not in report
    assert "`BAD` -> UNSUPPORTED" in report
    assert "Blocked claims (not rendered as facts)" in report
    assert "## Final Status: BLOCKED" in report


def test_claim_decision_itself_is_recorded_as_evidence(tmp_path: Path):
    repo = _repo(tmp_path)
    evidence = append_evidence_event(repo, event_type="token_usage", source="token_ledger", status="recorded")

    result = evaluate_and_record_claim(
        repo,
        {
            "claim_id": "C9",
            "claim_type": "token_usage_recorded",
            "text": "Token usage was recorded",
            "evidence_event_ids": [evidence["event_id"]],
        },
    )
    rows = read_evidence_ledger(repo)

    assert result["status"] == SUPPORTED
    assert result["decision_recorded"] is True
    assert rows[-1]["event_id"] == result["decision_event_id"]
    assert rows[-1]["event_type"] == "claim_decision"
    assert rows[-1]["data"]["decision"] == SUPPORTED
