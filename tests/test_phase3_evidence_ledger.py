import json
from pathlib import Path

from uacos.agent.task import create_task
from uacos.execution.artifacts import ingest_agent_output
from uacos.execution.evidence_ledger import (
    append_evidence_event,
    evidence_ledger_path,
    read_evidence_ledger,
    verify_evidence_ledger,
)
from uacos.execution.test_runner import run_task_tests
from uacos.execution.token_ledger import log_token_usage, read_ledger
from uacos.storage import init_storage


def test_evidence_ledger_hash_chain_is_valid(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)

    first = append_evidence_event(repo, event_type="context", source="test", status="recorded", task_id="T1")
    second = append_evidence_event(
        repo,
        event_type="test_command",
        source="test",
        status="pass",
        task_id="T1",
        parent_event_ids=[first["event_id"]],
    )

    rows = read_evidence_ledger(repo)
    verification = verify_evidence_ledger(repo)

    assert [row["seq"] for row in rows] == [1, 2]
    assert second["prev_hash"] == first["event_hash"]
    assert second["parent_event_ids"] == [first["event_id"]]
    assert verification["status"] == "pass"
    assert verification["records"] == 2
    assert verification["head_hash"] == second["event_hash"]


def test_evidence_ledger_detects_tampering(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)
    append_evidence_event(repo, event_type="test_command", source="test", status="pass", data={"tests": 1})

    path = evidence_ledger_path(repo)
    row = json.loads(path.read_text(encoding="utf-8"))
    row["data"]["tests"] = 999
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    verification = verify_evidence_ledger(repo)
    assert verification["status"] == "fail"
    assert verification["reason"] == "payload_hash_mismatch:1"


def test_token_ledger_preserves_legacy_record_and_adds_canonical_event(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)

    record = log_token_usage(repo, "TASK-X", "coder", "local-test", 100, 50, "CTX-X")
    legacy = read_ledger(repo)
    events = read_evidence_ledger(repo)

    assert len(legacy) == 1
    assert legacy[0]["task_id"] == "TASK-X"
    assert record["evidence_event_id"] == events[0]["event_id"]
    assert events[0]["event_type"] == "token_usage"
    assert events[0]["token_usage"]["input_tokens"] == 100
    assert events[0]["evidence_refs"] == ["CTX-X"]
    assert verify_evidence_ledger(repo)["status"] == "pass"


def test_real_task_test_runner_records_each_host_observed_result(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "script.py").write_text("print('ok')\n", encoding="utf-8")
    init_storage(repo)
    task_file = create_task(
        repo,
        "Run evidence tests",
        "Record safe and blocked commands",
        allowed_files=["script.py"],
        tests=["python script.py", "rm -rf /"],
    )

    result = run_task_tests(repo, task_file)
    events = read_evidence_ledger(repo)

    assert result["status"] == "fail"
    assert len(result["evidence_event_ids"]) == 2
    assert [event["event_type"] for event in events] == ["test_command", "test_command"]
    assert {event["status"] for event in events} == {"pass", "blocked"}
    assert all(event["task_id"] == result["task_id"] for event in events)
    assert verify_evidence_ledger(repo)["status"] == "pass"


def test_agent_artifact_is_persisted_and_bound_to_diff_hash_event(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return False\n", encoding="utf-8")
    init_storage(repo)
    task_file = create_task(repo, "Fix ok", "Fix ok return value", allowed_files=["app.py"])
    agent_output = repo / "agent.md"
    agent_output.write_text(
        "```diff\n"
        "diff --git a/app.py b/app.py\n"
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def ok():\n"
        "-    return False\n"
        "+    return True\n"
        "```\n",
        encoding="utf-8",
    )

    artifact = ingest_agent_output(repo, task_file, agent_output)
    events = read_evidence_ledger(repo)
    persisted = json.loads(Path(artifact["artifact_file"]).read_text(encoding="utf-8"))

    assert artifact["status"] == "pass"
    assert Path(artifact["artifact_file"]).exists()
    assert Path(artifact["diff_file"]).exists()
    assert persisted["evidence_event_id"] == artifact["evidence_event_id"]
    assert events[-1]["event_id"] == artifact["evidence_event_id"]
    assert events[-1]["event_type"] == "agent_artifact"
    assert events[-1]["diff_hash"]
    assert artifact["artifact_file"] in events[-1]["evidence_refs"]
    assert verify_evidence_ledger(repo)["status"] == "pass"
