from datetime import datetime, timedelta, timezone
from pathlib import Path

from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.security.approval import create_approval_record, verify_approval_record
from uacos.security.patch_review import review_patch_text
from uacos.security.policy import evaluate_patch_policy, load_policy


PATCH = """diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -1 +1 @@
-TOKEN = 'old'
+TOKEN = 'new'
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


def _policy(path: Path) -> Path:
    path.write_text(
        """version: 1
default_action: allow
approval:
  required_risk_levels: [high, critical]
  required_categories: [auth_change]
  ttl_seconds: 600
deny:
  risk_levels: [block]
  categories: []
""",
        encoding="utf-8",
    )
    return path


def test_yaml_policy_requires_approval_for_high_risk_patch(tmp_path: Path):
    policy = load_policy(_policy(tmp_path / "policy.yaml"))
    review = {
        "risk_level": "high",
        "risk_categories": ["auth_change"],
        "semantic_risk": {"categories": ["security_sensitive_symbol"]},
    }
    decision = evaluate_patch_policy(review, policy)
    assert decision["action"] == "approval_required"
    assert decision["requires_approval"] is True
    assert decision["policy_sha256"] == policy["policy_sha256"]


def test_approval_is_bound_to_patch_policy_and_expiry(tmp_path: Path):
    policy = load_policy(_policy(tmp_path / "policy.yaml"))
    decision = evaluate_patch_policy(
        {"risk_level": "high", "risk_categories": ["auth_change"], "semantic_risk": None},
        policy,
    )
    now = datetime(2026, 10, 3, tzinfo=timezone.utc)
    record = create_approval_record(PATCH, decision, approved_by="reviewer@example", now=now)

    assert verify_approval_record(record, PATCH, decision, now=now + timedelta(seconds=30))["status"] == "pass"
    assert "patch_hash_mismatch" in verify_approval_record(record, PATCH + "\n", decision, now=now)["findings"]
    assert "approval_expired" in verify_approval_record(record, PATCH, decision, now=now + timedelta(seconds=601))["findings"]


def test_safe_execution_blocks_high_risk_patch_without_human_approval(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text("TOKEN = 'old'\n", encoding="utf-8")
    policy_path = _policy(repo / "policy.yaml")

    result = run_safe_agent_execution(
        repo,
        "rotate auth token",
        PatchAdapter(),
        allowed_files=["auth.py"],
        max_iterations=1,
        policy_path=policy_path,
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "human_approval_required"
    assert result["policy_decision"]["action"] == "approval_required"
    assert result["patch_apply"] is None
    assert (repo / "auth.py").read_text(encoding="utf-8") == "TOKEN = 'old'\n"


def test_valid_human_approval_allows_guarded_apply(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text("TOKEN = 'old'\n", encoding="utf-8")
    policy_path = _policy(repo / "policy.yaml")

    policy = load_policy(policy_path)
    review = review_patch_text(PATCH, allowed_files=["auth.py"], repo_root=repo)
    decision = evaluate_patch_policy(review, policy)
    approval = create_approval_record(PATCH, decision, approved_by="human-reviewer")

    result = run_safe_agent_execution(
        repo,
        "rotate auth token",
        PatchAdapter(),
        allowed_files=["auth.py"],
        tests=["python -c \"from pathlib import Path; assert 'new' in Path('auth.py').read_text()\""],
        max_iterations=1,
        policy_path=policy_path,
        approval_record=approval,
    )

    assert result["status"] == "passed"
    assert result["approval_verification"]["status"] == "pass"
    assert (repo / "auth.py").read_text(encoding="utf-8") == "TOKEN = 'new'\n"


def test_invalid_policy_fails_closed_before_apply(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "auth.py").write_text("TOKEN = 'old'\n", encoding="utf-8")
    policy_path = repo / "policy.yaml"
    policy_path.write_text("version: 999\n", encoding="utf-8")

    result = run_safe_agent_execution(
        repo,
        "rotate auth token",
        PatchAdapter(),
        allowed_files=["auth.py"],
        max_iterations=1,
        policy_path=policy_path,
    )
    assert result["status"] == "blocked"
    assert result["reason"] == "policy_load_failed"
    assert result["patch_apply"] is None
