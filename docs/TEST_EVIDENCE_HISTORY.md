# UACOS Test Evidence History

This file consolidates historical phase test reports and end-to-end validation reports.

Generated: 2026-05-02T06:10:38.579111+00:00

## Source Files

- `PHASE_2_TEST_REPORT.md` - Phase 2 Test Report
- `PHASE_3_TEST_REPORT.md` - Phase 3 Test Report
- `PHASE_4_TEST_REPORT.md` - Phase 4 Test Report
- `PHASE_5_TEST_REPORT.md` - Phase 5 Test Report
- `PHASE_6_TEST_REPORT.md` - Phase 6 Test Report
- `PHASE_7_TEST_REPORT.md` - Phase 7 Test Report
- `PHASE_8_TEST_REPORT.md` - Phase 8 Test Report
- `PHASE_9_TEST_REPORT.md` - Phase 9 Test Report
- `PHASE_10_TEST_REPORT.md` - Phase 10 Test Report
- `PHASE_11_TEST_REPORT.md` - Phase 11 Test Report
- `PHASE_12_TEST_REPORT.md` - Phase 12 Test Report
- `PHASE_13_TEST_REPORT.md` - Phase 13 Test Report
- `PHASE_14_TEST_REPORT.md` - Phase 14 Test Report
- `PHASE_16_TEST_REPORT.md` - Phase 16 Test Report
- `PHASE_17_TEST_REPORT.md` - Phase 17 Test Report
- `PHASE_18_TEST_REPORT.md` - Phase 18 Test Report
- `PHASE_19_TEST_REPORT.md` - Phase 19 Test Report
- `PHASE_20_TEST_REPORT.md` - Phase 20 Test Report
- `PHASE_21_TEST_REPORT.md` - Phase 21 Test Report
- `PHASE_22_TEST_REPORT.md` - Phase 22 Test Report
- `PHASE_23_TEST_REPORT.md` - Phase 23 Test Report
- `PHASE_24_TEST_REPORT.md` - Phase 24 Test Report
- `PHASE_25_TEST_REPORT.md` - Phase 25 Test Report
- `PHASE_26_TEST_REPORT.md` - Phase 26 Test Report
- `PHASE_27_TEST_REPORT.md` - Phase 27 Test Report
- `PHASE_28_TEST_REPORT.md` - Phase 28 Test Report
- `PHASE_29_TEST_REPORT.md` - Phase 29 Test Report
- `PHASE_30_TEST_REPORT.md` - Phase 30 Test Report
- `PHASE_31_TEST_REPORT.md` - Phase 31 Test Report
- `PHASE_32_TEST_REPORT.md` - Phase 32 Test Report
- `V1_END_TO_END_VALIDATION_REPORT.md` - UACOS v1 End-to-End Validation Report
- `V2_END_TO_END_VALIDATION_REPORT.md` - V2 E2E Validation

## Consolidated Content

---

## Source: `PHASE_2_TEST_REPORT.md`

# Phase 2 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                                       [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m2 passed\u001b[0m\u001b[32m in 0.21s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE2_SMOKE_OK\nscan= {'scan_run_id': 1, 'files_seen': 2, 'files_indexed': 2, 'files_skipped': 0, 'files_changed': 2, 'symbols_indexed': 6, 'started_at': '2026-04-26T08:33:26.180658+00:00', 'finished_at': '2026-04-26T08:33:26.185350+00:00'}\nstats= {'file_count': 2, 'symbol_count': 6, 'languages': [{'language': 'python', 'c': 1}, {'language': 'html', 'c': 1}], 'symbol_kinds': [{'kind': 'function', 'c': 2}, {'kind': 'class_attr', 'c': 2}, {'kind': 'id', 'c': 1}, {'kind': 'class', 'c': 1}], 'last_scan': {'id': 1, 'started_at': '2026-04-26T08:33:26.180658+00:00', 'finished_at': '2026-04-26T08:33:26.184216+00:00', 'repo_path': '/tmp/tmpiqg9_296/sample_repo', 'files_seen': 2, 'files_indexed': 2, 'files_skipped': 0, 'files_changed': 2, 'symbols_indexed': 6}}\ncontext_id= ce5d7fb4ba1556325c715cfc\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_help_returncode": 0,
  "cli_help_stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats} ...\n\nUniversal AI Context OS - Phase 2 MVP\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats}\n\noptions:\n  -h, --help            show this help message and exit\n",
  "cli_help_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_3_TEST_REPORT.md`

# Phase 3 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                                    [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m5 passed\u001b[0m\u001b[32m in 0.19s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE3_SMOKE_OK\nsecurity_findings= 1\npatch_status= pass\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_command_check_returncode": 0,
  "cli_command_check_stdout": "{\n  \"allowed\": true,\n  \"reason\": \"allowed\",\n  \"command\": \"pytest -q\"\n}\n",
  "cli_command_check_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_4_TEST_REPORT.md`

# Phase 4 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                                  [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m7 passed\u001b[0m\u001b[32m in 0.26s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE4_SMOKE_OK\nrun_id= RUN-33c7dce5bb69\ncontext_id= 55b539849494875633841a42\nsteps= 4\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_agent_list_returncode": 0,
  "cli_agent_list_stdout": "{\n  \"agents\": [\n    {\n      \"name\": \"planner\",\n      \"role\": \"planner\",\n      \"adapter\": \"dry_run\",\n      \"model\": \"local\",\n      \"priority\": 10,\n      \"can_edit\": false,\n      \"can_run_commands\": false,\n      \"description\": \"Breaks task into safe plan and context requirements.\"\n    },\n    {\n      \"name\": \"coder\",\n      \"role\": \"coder\",\n      \"adapter\": \"dry_run\",\n      \"model\": \"local\",\n      \"priority\": 20,\n      \"can_edit\": true,\n      \"can_run_commands\": false,\n      \"description\": \"Produces patch proposal within allowed scope.\"\n    },\n    {\n      \"name\": \"reviewer\",\n      \"role\": \"reviewer\",\n      \"adapter\": \"dry_run\",\n      \"model\": \"local\",\n      \"priority\": 30,\n      \"can_edit\": false,\n      \"can_run_commands\": false,\n      \"description\": \"Reviews patch and scope/security risks.\"\n    },\n    {\n      \"name\": \"tester\",\n      \"role\": \"tester\",\n      \"adapter\": \"dry_run\",\n      \"model\": \"local\",\n      \"priority\": 40,\n      \"can_edit\": false,\n      \"can_run_commands\": true,\n      \"description\": \"Runs approved tests/commands only.\"\n    }\n  ]\n}\n",
  "cli_agent_list_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_5_TEST_REPORT.md`

# Phase 5 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                               [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m10 passed\u001b[0m\u001b[32m in 0.36s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE5_SMOKE_OK\nmanual_context= /tmp/tmp0c_fp4xo/repo/context_for_chatgpt_claude.md\nopenclaw_status= dry_run\nollama_status= dry_run\nmcp_manifest= /tmp/tmp0c_fp4xo/repo/.uacos/mcp_manifest.json\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_adapter_list_returncode": 0,
  "cli_adapter_list_stdout": "{\n  \"version\": 1,\n  \"default_dry_run\": true,\n  \"adapters\": {\n    \"manual_chat\": {\n      \"enabled\": true,\n      \"type\": \"export\",\n      \"dry_run\": true,\n      \"description\": \"Exports context pack for ChatGPT/Claude web/manual paste.\"\n    },\n    \"openclaw_cli\": {\n      \"enabled\": true,\n      \"type\": \"cli\",\n      \"dry_run\": true,\n      \"command_template\": \"/home/aiserver/ai-team/executor/chat.sh {agent} {prompt_file}\",\n      \"default_agent\": \"leader\",\n      \"timeout_seconds\": 120,\n      \"description\": \"Runs OpenClaw through a local CLI wrapper.\"\n    },\n    \"aider_cli\": {\n      \"enabled\": true,\n      \"type\": \"cli\",\n      \"dry_run\": true,\n      \"command_template\": \"aider --message-file {prompt_file}\",\n      \"timeout_seconds\": 120,\n      \"description\": \"Runs Aider CLI with a prompt file.\"\n    },\n    \"ollama_openai\": {\n      \"enabled\": true,\n      \"type\": \"openai_compatible\",\n      \"dry_run\": true,\n      \"base_url\": \"http://localhost:11434/v1/chat/completions\",\n      \"model\": \"qwen2.5-coder:7b\",\n      \"timeout_seconds\": 120,\n      \"description\": \"Calls local Ollama/OpenAI-compatible chat endpoint.\"\n    },\n    \"cline_roo_mcp\": {\n      \"enabled\": true,\n      \"type\": \"mcp_manifest\",\n      \"dry_run\": true,\n      \"description\": \"Exports MCP manifest skeleton for Cline/Roo compatible agents.\"\n    }\n  }\n}\n",
  "cli_adapter_list_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_6_TEST_REPORT.md`

# Phase 6 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                            [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m13 passed\u001b[0m\u001b[32m in 6.06s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE6_SMOKE_OK\nartifact_status= pass\ntest_status= pass\ntoken_records= 1\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_extract_diff_returncode": 0,
  "cli_extract_diff_stdout": "{\n  \"status\": \"fail\",\n  \"has_diff\": false,\n  \"output\": null,\n  \"diff\": \"\"\n}\n",
  "cli_extract_diff_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_7_TEST_REPORT.md`

# Phase 7 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                         [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m16 passed\u001b[0m\u001b[32m in 23.65s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE7_SMOKE_OK\nmanifest= /tmp/tmpmv1xiqws/repo/.uacos/change_manifests/CHANGE-91caade70705.json\ndone_gate= done\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_manifest_list_returncode": 0,
  "cli_manifest_list_stdout": "{\n  \"count\": 0,\n  \"manifests\": []\n}\n",
  "cli_manifest_list_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_8_TEST_REPORT.md`

# Phase 8 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                      [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m19 passed\u001b[0m\u001b[32m in 24.92s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE8_SMOKE_OK\nmemories= 2\nregression_status= fail\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_memory_list_returncode": 0,
  "cli_memory_list_stdout": "{\n  \"memories\": []\n}\n",
  "cli_memory_list_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_9_TEST_REPORT.md`

# Phase 9 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                    [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m21 passed\u001b[0m\u001b[32m in 25.24s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE9_SMOKE_OK\nrepo= /tmp/tmpy10bn2b3/repo\nmemory_count= 1\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_ops_summary_returncode": 0,
  "cli_ops_summary_stdout": "{\n  \"repo\": \"/mnt/data/uacos_phase9_mvp\",\n  \"uacos_dir\": \"/mnt/data/uacos_phase9_mvp/.uacos\",\n  \"stats\": {\n    \"file_count\": 0,\n    \"symbol_count\": 0,\n    \"languages\": [],\n    \"symbol_kinds\": [],\n    \"last_scan\": null\n  },\n  \"memory_count\": 0,\n  \"active_memory_count\": 0,\n  \"failure_count\": 0,\n  \"manifest_count\": 0,\n  \"token_summary\": {\n    \"records\": 0,\n    \"input_tokens\": 0,\n    \"output_tokens\": 0,\n    \"estimated_cost_usd\": 0,\n    \"by_agent\": {},\n    \"by_model\": {}\n  }\n}\n",
  "cli_ops_summary_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_10_TEST_REPORT.md`

# Phase 10 Test Report

```json
{
  "pytest_returncode": 0,
  "pytest_stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                 [100%]\u001b[0m\n\u001b[32m\u001b[32m\u001b[1m24 passed\u001b[0m\u001b[32m in 25.11s\u001b[0m\u001b[0m\n",
  "pytest_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "smoke_returncode": 0,
  "smoke_stdout": "PHASE10_SMOKE_OK\nhealth= pass\nbackup= /tmp/tmpz6756etq/backup.zip\nrelease= pass\n",
  "smoke_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n",
  "cli_health_returncode": 0,
  "cli_health_stdout": "{\n  \"status\": \"pass\",\n  \"checks\": [\n    {\n      \"name\": \"repo_exists\",\n      \"ok\": true,\n      \"detail\": \"/mnt/data/uacos_phase10_mvp\"\n    },\n    {\n      \"name\": \"uacos_dir_exists\",\n      \"ok\": true,\n      \"detail\": \"/mnt/data/uacos_phase10_mvp/.uacos\"\n    },\n    {\n      \"name\": \"db_exists\",\n      \"ok\": true,\n      \"detail\": \"/mnt/data/uacos_phase10_mvp/.uacos/repo_index.sqlite\"\n    },\n    {\n      \"name\": \"agents_config_exists\",\n      \"ok\": true,\n      \"detail\": \"/mnt/data/uacos_phase10_mvp/.uacos/agents.json\"\n    },\n    {\n      \"name\": \"adapters_config_exists\",\n      \"ok\": true,\n      \"detail\": \"/mnt/data/uacos_phase10_mvp/.uacos/adapters.json\"\n    },\n    {\n      \"name\": \"ops_summary_ok\",\n      \"ok\": true,\n      \"detail\": \"{\\\"repo\\\": \\\"/mnt/data/uacos_phase10_mvp\\\", \\\"uacos_dir\\\": \\\"/mnt/data/uacos_phase10_mvp/.uacos\\\", \\\"stats\\\": {\\\"file_count\\\": 0, \\\"symbol_count\\\": 0, \\\"languages\\\": [], \\\"symbol_kinds\\\": [], \\\"last_scan\\\": null}, \\\"memory_count\\\": 0, \\\"active_memory_count\\\": 0, \\\"failure_count\\\": 0, \\\"manifest_count\\\": 0, \\\"token_summary\\\": {\\\"records\\\": 0, \\\"input_tokens\\\": 0, \\\"output_tokens\\\": 0, \\\"estimated_cost_usd\\\": 0, \\\"by_agent\\\": {}, \\\"by_model\\\": {}}}\"\n    }\n  ],\n  \"created_at\": \"2026-04-26T12:26:22.530473+00:00\"\n}\n",
  "cli_health_stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
}
```

---

## Source: `PHASE_11_TEST_REPORT.md`

# Phase 11 Test Report

```json
{
  "phase11_direct_validation": {
    "status": "pass",
    "validated": [
      "skill_add_search",
      "skill_lifecycle",
      "skill_extract",
      "context_injection",
      "reject"
    ]
  },
  "cli_workflow": [
    {
      "cmd": "uacos.cli bootstrap --repo /tmp/uacos_phase11_cli_test",
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/tmp/uacos_phase11_cli_test\",\n  \"db\": \"/tmp/uacos_phase11_cli_test/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/tmp/uacos_phase11_cli_test/.uacos/agents.json\",\n  \"adapter_config\": \"/tmp/uacos_phase11_cli_test/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-27T14:32:19.778783+00:00\",\n    \"finished_at\": \"2026-04-27T14:32:19.868039+00:00\"\n  },\n  \"created_at\": \"2026-04-27T14:32:19.868148+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": "uacos.cli skill-add --repo /tmp/uacos_phase11_cli_test --title Fix Python venv mismatch --problem unsupported operand type --problem Python39 --root-cause old Python --solution use Python 3.12 --command py -3.12 -m venv .venv --status approved",
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKILL-b665b6913f10\",\n  \"title\": \"Fix Python venv mismatch\",\n  \"category\": \"general\",\n  \"problem_signatures\": [\n    \"unsupported operand type\",\n    \"Python39\"\n  ],\n  \"root_cause\": \"old Python\",\n  \"solution_steps\": [\n    \"use Python 3.12\"\n  ],\n  \"commands\": [\n    \"py -3.12 -m venv .venv\"\n  ],\n  \"verification\": [],\n  \"applies_to\": [],\n  \"source\": \"user\",\n  \"confidence\": 0.8,\n  \"status\": \"approved\",\n  \"tags\": [],\n  \"times_used\": 0,\n  \"last_used_at\": null,\n  \"created_at\": \"2026-04-27T14:32:23.375281+00:00\",\n  \"updated_at\": \"2026-04-27T14:32:23.375374+00:00\",\n  \"deprecated_reason\": null,\n  \"reject_reason\": null\n}\n",
      "stderr": ""
    },
    {
      "cmd": "uacos.cli skill-suggest --repo /tmp/uacos_phase11_cli_test --task unsupported operand type Python39",
      "returncode": 0,
      "stdout": "{\n  \"task\": \"unsupported operand type Python39\",\n  \"skills\": [\n    {\n      \"id\": \"SKILL-b665b6913f10\",\n      \"title\": \"Fix Python venv mismatch\",\n      \"category\": \"general\",\n      \"problem_signatures\": [\n        \"unsupported operand type\",\n        \"Python39\"\n      ],\n      \"root_cause\": \"old Python\",\n      \"solution_steps\": [\n        \"use Python 3.12\"\n      ],\n      \"commands\": [\n        \"py -3.12 -m venv .venv\"\n      ],\n      \"verification\": [],\n      \"applies_to\": [],\n      \"source\": \"user\",\n      \"confidence\": 0.8,\n      \"status\": \"approved\",\n      \"tags\": [],\n      \"times_used\": 0,\n      \"last_used_at\": null,\n      \"created_at\": \"2026-04-27T14:32:23.375281+00:00\",\n      \"updated_at\": \"2026-04-27T14:32:23.375374+00:00\",\n      \"deprecated_reason\": null,\n      \"reject_reason\": null,\n      \"_score\": 8.8\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": "uacos.cli context --repo /tmp/uacos_phase11_cli_test --task unsupported operand type Python39",
      "returncode": 0,
      "stdout": "{\n  \"id\": \"f0847c4d0f6a7e109ab6e36a\",\n  \"token_count\": 198,\n  \"content\": \"# UACOS Context Pack v0\\n\\n## Task\\nunsupported operand type Python39\\n\\n## Relevant Memory\\nNo active project memories matched this task.\\n\\n## Relevant Skills\\n# Relevant Reusable Skills\\n\\n- [approved] Fix Python venv mismatch (id=SKILL-b665b6913f10, score=8.8, used=0)\\n  - signatures: unsupported operand type, Python39\\n  - solution: use Python 3.12\\n  - commands: py -3.12 -m venv .venv\\n\\n\\n## Operating Rules\\n- Use this context instead of reading the whole repository.\\n- Do not access secret-like files such as `.env`, `*.pem`, `*.key`.\\n- Ask for scope expansion if more files are required.\\n- Do not claim DONE without tests or explicit validation evidence.\\n\\n## Repo Map\\n# Repo Map\\n\\nQuery: unsupported operand type Python39\\n\\n## app.py\\n- L1-L2 `function` **ok** — def ok():\\n\\n\\n## Search Hits\\n\\n## Snippets\\n\"\n}\n",
      "stderr": ""
    }
  ],
  "cli_help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills} ...\n\nUniversal AI Context OS v1.1 - Phase 11 Skill Memory Engine\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills}\n\noptions:\n  -h, --help            show this help message and exit\n",
    "stderr": ""
  },
  "version": {
    "returncode": 0,
    "stdout": "1.1.0"
  }
}
```

---

## Source: `PHASE_12_TEST_REPORT.md`

# Phase 12 Test Report

```json
{
  "direct_checks": {
    "vscode_status_ok": true,
    "extension_status_ok": true,
    "workspace_status_ok": true,
    "tasks_has_health": true,
    "tasks_has_skill_review": true,
    "tasks_has_port": true,
    "settings_port_ok": true,
    "launch_module_ok": true,
    "extension_has_skill_suggest": true,
    "workspace_path_ok": true
  },
  "cli_checks": {
    "all_cli_returncode_zero": true,
    "cli_tasks_exists": true,
    "cli_extension_exists": true,
    "cli_workspace_exists": true,
    "cli_tasks_has_port": true
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "--help"
      ],
      "returncode": 0,
      "stdout": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace} ...\n\nUniversal AI Context OS v1.2 - Phase 12 VSCode Integration Layer\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-syste",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "vscode-init",
        "--repo",
        "/mnt/data/uacos_phase12_cli_fast_repo",
        "--port",
        "8877",
        "--overwrite"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"vscode_dir\": \"/mnt/data/uacos_phase12_cli_fast_repo/.vscode\",\n  \"files\": [\n    {\n      \"path\": \"/mnt/data/uacos_phase12_cli_fast_repo/.vscode/tasks.json\",\n      \"status\": \"written\"\n    },\n    {\n      \"path\": \"/mnt/data/uacos_phase12_cli_fast_repo/.vscode/settings.json\",\n      \"status\": \"written\"\n    },\n    {\n      \"path\": \"/mnt/data/uacos_phase12_cli_fast_repo/.vscode/launch.json\",\n      \"status\": \"written\"\n    }\n  ],\n  \"created_at\": \"2026-04-27T14:50:17.585863+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "vscode-extension-skeleton",
        "--output-dir",
        "/mnt/data/uacos_phase12_cli_fast_ext",
        "--overwrite"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"output_dir\": \"/mnt/data/uacos_phase12_cli_fast_ext\",\n  \"files\": [\n    \"/mnt/data/uacos_phase12_cli_fast_ext/package.json\",\n    \"/mnt/data/uacos_phase12_cli_fast_ext/extension.js\",\n    \"/mnt/data/uacos_phase12_cli_fast_ext/README.md\"\n  ],\n  \"created_at\": \"2026-04-27T14:50:21.187181+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "vscode-workspace",
        "--repo",
        "/mnt/data/uacos_phase12_cli_fast_repo",
        "--output",
        "/mnt/data/uacos_phase12_cli_fast_repo/project.code-workspace",
        "--port",
        "8877"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"workspace_file\": \"/mnt/data/uacos_phase12_cli_fast_repo/project.code-workspace\"\n}\n",
      "stderr": ""
    }
  ],
  "vscode_result": {
    "status": "ok",
    "vscode_dir": "/mnt/data/uacos_phase12_direct_test_repo/.vscode",
    "files": [
      {
        "path": "/mnt/data/uacos_phase12_direct_test_repo/.vscode/tasks.json",
        "status": "written"
      },
      {
        "path": "/mnt/data/uacos_phase12_direct_test_repo/.vscode/settings.json",
        "status": "written"
      },
      {
        "path": "/mnt/data/uacos_phase12_direct_test_repo/.vscode/launch.json",
        "status": "written"
      }
    ],
    "created_at": "2026-04-27T14:50:13.483973+00:00"
  },
  "extension_result": {
    "status": "ok",
    "output_dir": "/mnt/data/uacos_phase12_direct_extension",
    "files": [
      "/mnt/data/uacos_phase12_direct_extension/package.json",
      "/mnt/data/uacos_phase12_direct_extension/extension.js",
      "/mnt/data/uacos_phase12_direct_extension/README.md"
    ],
    "created_at": "2026-04-27T14:50:13.486867+00:00"
  },
  "workspace_result": {
    "status": "ok",
    "workspace_file": "/mnt/data/uacos_phase12_direct_test_repo/project.code-workspace"
  }
}
```

---

## Source: `PHASE_13_TEST_REPORT.md`

# Phase 13 Test Report

```json
{
  "base_zip": "/mnt/data/uacos_phase12_vscode_integration.zip",
  "checks": {
    "smoke_ok": true,
    "help_ok": true,
    "cli_base_ok": true,
    "skill_id_found": true,
    "approve_ok": true,
    "suggest_ok": true,
    "context_injects_skill": true,
    "learning_events_file_exists": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE13_SMOKE_OK\nskill= SKILL-2d55d3993755\nevents= 1\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list} ...\n\nUniversal AI Context OS v1.3 - Phase 13 Auto-Learning Loop\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list}\n\noptions:\n  -h, --help            show this help message and exit\n",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase13_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase13_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase13_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase13_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase13_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 2,\n    \"files_indexed\": 2,\n    \"files_skipped\": 0,\n    \"files_changed\": 2,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-27T14:58:33.572542+00:00\",\n    \"finished_at\": \"2026-04-27T14:58:33.594906+00:00\"\n  },\n  \"created_at\": \"2026-04-27T14:58:33.595013+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "learn-from-evidence",
        "--repo",
        "/mnt/data/uacos_phase13_cli_repo",
        "--source-file",
        "/mnt/data/uacos_phase13_cli_repo/evidence.md",
        "--title",
        "Fix Python venv mismatch"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"classification\": {\n    \"kind\": \"failure\",\n    \"severity\": \"high\"\n  },\n  \"skill\": {\n    \"id\": \"SKILL-4924c62dfc10\",\n    \"title\": \"Fix Python venv mismatch\",\n    \"category\": \"evidence_learning\",\n    \"problem_signatures\": [\n      \"TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\",\n      \"unsupported operand\"\n    ],\n    \"root_cause\": \"Root cause: Python 3.9 venv is too old.\",\n    \"solution_steps\": [\n      \"Fix: use Python 3.12 venv.\"\n    ],\n    \"commands\": [\n      \"py -3.12 -m venv .venv\"\n    ],\n    \"verification\": [],\n    \"applies_to\": [],\n    \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n    \"confidence\": 0.65,\n    \"status\": \"candidate\",\n    \"tags\": [\n      \"auto_extracted\"\n    ],\n    \"times_used\": 0,\n    \"last_used_at\": null,\n    \"created_at\": \"2026-04-27T14:58:37.686817+00:00\",\n    \"updated_at\": \"2026-04-27T14:58:37.686894+00:00\",\n    \"deprecated_reason\": null,\n    \"reject_reason\": null\n  },\n  \"memory\": {\n    \"id\": \"MEM-d08d420a1b2c\",\n    \"kind\": \"failure\",\n    \"key\": \"fix_python_venv_mismatch\",\n    \"value\": \"Root cause: Python 3.9 venv is too old.\\nTypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\\nFix: use Python 3.12 venv.\\npy -3.12 -m venv .venv\",\n    \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n    \"confidence\": 0.75,\n    \"tags\": [\n      \"auto_learning\",\n      \"failure\",\n      \"high\"\n    ],\n    \"applies_to\": [],\n    \"valid_at\": \"2026-04-27T14:58:37.688445+00:00\",\n    \"invalid_at\": null,\n    \"invalid_reason\": null,\n    \"created_at\": \"2026-04-27T14:58:37.688461+00:00\",\n    \"updated_at\": \"2026-04-27T14:58:37.688465+00:00\"\n  },\n  \"duplicates\": [],\n  \"event\": {\n    \"event\": \"learn_from_text\",\n    \"title\": \"Fix Python venv mismatch\",\n    \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n    \"classification\": {\n      \"kind\": \"failure\",\n      \"severity\": \"high\"\n    },\n    \"skill_id\": \"SKILL-4924c62dfc10\",\n    \"skill_status\": \"candidate\",\n    \"memory_id\": \"MEM-d08d420a1b2c\",\n    \"duplicate_skill_candidates\": [],\n    \"ts\": \"2026-04-27T14:58:37.690177+00:00\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "learn-review",
        "--repo",
        "/mnt/data/uacos_phase13_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"candidate_skill_count\": 1,\n  \"candidate_skills\": [\n    {\n      \"id\": \"SKILL-4924c62dfc10\",\n      \"title\": \"Fix Python venv mismatch\",\n      \"category\": \"evidence_learning\",\n      \"problem_signatures\": [\n        \"TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\",\n        \"unsupported operand\"\n      ],\n      \"root_cause\": \"Root cause: Python 3.9 venv is too old.\",\n      \"solution_steps\": [\n        \"Fix: use Python 3.12 venv.\"\n      ],\n      \"commands\": [\n        \"py -3.12 -m venv .venv\"\n      ],\n      \"verification\": [],\n      \"applies_to\": [],\n      \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n      \"confidence\": 0.65,\n      \"status\": \"candidate\",\n      \"tags\": [\n        \"auto_extracted\"\n      ],\n      \"times_used\": 0,\n      \"last_used_at\": null,\n      \"created_at\": \"2026-04-27T14:58:37.686817+00:00\",\n      \"updated_at\": \"2026-04-27T14:58:37.686894+00:00\",\n      \"deprecated_reason\": null,\n      \"reject_reason\": null\n    }\n  ],\n  \"auto_memory_count\": 1,\n  \"auto_memories\": [\n    {\n      \"id\": \"MEM-d08d420a1b2c\",\n      \"kind\": \"failure\",\n      \"key\": \"fix_python_venv_mismatch\",\n      \"value\": \"Root cause: Python 3.9 venv is too old.\\nTypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\\nFix: use Python 3.12 venv.\\npy -3.12 -m venv .venv\",\n      \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n      \"confidence\": 0.75,\n      \"tags\": [\n        \"auto_learning\",\n        \"failure\",\n        \"high\"\n      ],\n      \"applies_to\": [],\n      \"valid_at\": \"2026-04-27T14:58:37.688445+00:00\",\n      \"invalid_at\": null,\n      \"invalid_reason\": null,\n      \"created_at\": \"2026-04-27T14:58:37.688461+00:00\",\n      \"updated_at\": \"2026-04-27T14:58:37.688465+00:00\"\n    }\n  ],\n  \"learning_event_count\": 1,\n  \"recent_events\": [\n    {\n      \"event\": \"learn_from_text\",\n      \"title\": \"Fix Python venv mismatch\",\n      \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n      \"classification\": {\n        \"kind\": \"failure\",\n        \"severity\": \"high\"\n      },\n      \"skill_id\": \"SKILL-4924c62dfc10\",\n      \"skill_status\": \"candidate\",\n      \"memory_id\": \"MEM-d08d420a1b2c\",\n      \"duplicate_skill_candidates\": [],\n      \"ts\": \"2026-04-27T14:58:37.690177+00:00\"\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "learn-summary",
        "--repo",
        "/mnt/data/uacos_phase13_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"skills_total\": 1,\n  \"skills_by_status\": {\n    \"candidate\": 1\n  },\n  \"auto_learning_memories\": 1,\n  \"learning_events\": 1,\n  \"last_event\": {\n    \"event\": \"learn_from_text\",\n    \"title\": \"Fix Python venv mismatch\",\n    \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n    \"classification\": {\n      \"kind\": \"failure\",\n      \"severity\": \"high\"\n    },\n    \"skill_id\": \"SKILL-4924c62dfc10\",\n    \"skill_status\": \"candidate\",\n    \"memory_id\": \"MEM-d08d420a1b2c\",\n    \"duplicate_skill_candidates\": [],\n    \"ts\": \"2026-04-27T14:58:37.690177+00:00\"\n  }\n}\n",
      "stderr": ""
    }
  ],
  "skill_id": "SKILL-4924c62dfc10",
  "approve": {
    "returncode": 0,
    "stdout": "{\n  \"event\": \"status\",\n  \"skill_id\": \"SKILL-4924c62dfc10\",\n  \"status\": \"approved\",\n  \"reason\": \"\",\n  \"ts\": \"2026-04-27T14:58:47.768961+00:00\"\n}\n",
    "stderr": ""
  },
  "suggest": {
    "returncode": 0,
    "stdout": "{\n  \"task\": \"unsupported operand type Python39\",\n  \"skills\": [\n    {\n      \"id\": \"SKILL-4924c62dfc10\",\n      \"title\": \"Fix Python venv mismatch\",\n      \"category\": \"evidence_learning\",\n      \"problem_signatures\": [\n        \"TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\",\n        \"unsupported operand\"\n      ],\n      \"root_cause\": \"Root cause: Python 3.9 venv is too old.\",\n      \"solution_steps\": [\n        \"Fix: use Python 3.12 venv.\"\n      ],\n      \"commands\": [\n        \"py -3.12 -m venv .venv\"\n      ],\n      \"verification\": [],\n      \"applies_to\": [],\n      \"source\": \"/mnt/data/uacos_phase13_cli_repo/evidence.md\",\n      \"confidence\": 0.65,\n      \"status\": \"approved\",\n      \"tags\": [\n        \"auto_extracted\"\n      ],\n      \"times_used\": 0,\n      \"last_used_at\": null,\n      \"created_at\": \"2026-04-27T14:58:37.686817+00:00\",\n      \"updated_at\": \"2026-04-27T14:58:47.768961+00:00\",\n      \"deprecated_reason\": null,\n      \"reject_reason\": null,\n      \"_score\": 6.9\n    }\n  ]\n}\n",
    "stderr": ""
  },
  "context": {
    "returncode": 0,
    "stdout_head": "{\n  \"id\": \"f0847c4d0f6a7e109ab6e36a\",\n  \"token_count\": 269,\n  \"content\": \"# UACOS Context Pack v0\\n\\n## Task\\nunsupported operand type Python39\\n\\n## Relevant Memory\\n# Relevant Project Memory\\n\\n- [failure] fix_python_venv_mismatch: Root cause: Python 3.9 venv is too old.\\nTypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\\nFix: use Python 3.12 venv.\\npy -3.12 -m venv .venv (id=MEM-d08d420a1b2c, confidence=0.75)\\n\\n\\n## Relevant Skills\\n# Relevant Reusable Skills\\n\\n- [approved] Fix Python venv mismatch (id=SKILL-4924c62dfc10, score=6.9, used=0)\\n  - signatures: TypeError: unsupported operand type(s) for |: 'type' and 'NoneType', unsupported operand\\n  - solution: Fix: use Python 3.12 venv.\\n  - commands: py -3.12 -m venv .venv\\n\\n\\n## Operating Rules\\n- Use this context instead of reading the whole repository.\\n- Do not access secret-like files such as `.env`, `*.pem`, `*.key`.\\n- Ask for scope expansion if more files are required.\\n- Do not claim DONE without tests or explicit validation evidence.\\n\\n## Repo Map\\n# Repo Map\\n\\nQuery: unsupported operand type Python39\\n\\n## app.py\\n- L1-L2 `function` **ok** — def ok():\\n\\n\\n## Search Hits\\n\\n## Snippets\\n\"\n}\n",
    "stderr": ""
  }
}
```

---

## Source: `PHASE_14_TEST_REPORT.md`

# Phase 14 Test Report

```json
{
  "base_zip": "/mnt/data/uacos_phase13_auto_learning.zip",
  "checks": {
    "smoke_ok": true,
    "help_ok": true,
    "cli_all_ok": true,
    "semantic_index_file_exists": true,
    "semantic_search_has_skill": true,
    "semantic_context_has_skill": true,
    "normal_context_has_semantic_section": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE14_SMOKE_OK\nindex_docs= 2\ntop= Fix Python venv mismatch\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context} ...\n\nUniversal AI Context OS v1.4 - Phase 14 Semantic Memory Search\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context}\n\noptions:\n  -h, --help            show this help message and exit\n",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase14_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase14_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase14_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase14_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-27T15:04:49.976753+00:00\",\n    \"finished_at\": \"2026-04-27T15:04:49.985133+00:00\"\n  },\n  \"created_at\": \"2026-04-27T15:04:49.985210+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-add",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo",
        "--title",
        "Fix Python venv mismatch",
        "--problem",
        "unsupported operand type",
        "--problem",
        "NoneType",
        "--root-cause",
        "old Python runtime",
        "--solution",
        "use Python 3.12",
        "--status",
        "approved"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKILL-94f3940e0c9a\",\n  \"title\": \"Fix Python venv mismatch\",\n  \"category\": \"general\",\n  \"problem_signatures\": [\n    \"unsupported operand type\",\n    \"NoneType\"\n  ],\n  \"root_cause\": \"old Python runtime\",\n  \"solution_steps\": [\n    \"use Python 3.12\"\n  ],\n  \"commands\": [],\n  \"verification\": [],\n  \"applies_to\": [],\n  \"source\": \"user\",\n  \"confidence\": 0.8,\n  \"status\": \"approved\",\n  \"tags\": [],\n  \"times_used\": 0,\n  \"last_used_at\": null,\n  \"created_at\": \"2026-04-27T15:04:52.075926+00:00\",\n  \"updated_at\": \"2026-04-27T15:04:52.076015+00:00\",\n  \"deprecated_reason\": null,\n  \"reject_reason\": null\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "memory-add",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo",
        "--kind",
        "project_truth",
        "--key",
        "barrier_safety_roi",
        "--value",
        "Lower barrier must obey safe ROI",
        "--tag",
        "barrier",
        "--tag",
        "safety"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"MEM-251569dbb6ba\",\n  \"kind\": \"project_truth\",\n  \"key\": \"barrier_safety_roi\",\n  \"value\": \"Lower barrier must obey safe ROI\",\n  \"source\": \"user\",\n  \"confidence\": 1.0,\n  \"tags\": [\n    \"barrier\",\n    \"safety\"\n  ],\n  \"applies_to\": [],\n  \"valid_at\": \"2026-04-27T15:04:56.576615+00:00\",\n  \"invalid_at\": null,\n  \"invalid_reason\": null,\n  \"created_at\": \"2026-04-27T15:04:56.576709+00:00\",\n  \"updated_at\": \"2026-04-27T15:04:56.576714+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "semantic-index",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"index_file\": \"/mnt/data/uacos_phase14_cli_repo/.uacos/semantic_index.json\",\n  \"doc_count\": 2,\n  \"vocab_count\": 96,\n  \"provider\": \"local_tfidf\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "semantic-search",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo",
        "old python union type error"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"query\": \"old python union type error\",\n  \"provider\": \"local_tfidf\",\n  \"results\": [\n    {\n      \"id\": \"SKILL-94f3940e0c9a\",\n      \"type\": \"skill\",\n      \"title\": \"Fix Python venv mismatch\",\n      \"status\": \"approved\",\n      \"score\": 0.50884,\n      \"payload\": {\n        \"id\": \"SKILL-94f3940e0c9a\",\n        \"title\": \"Fix Python venv mismatch\",\n        \"category\": \"general\",\n        \"problem_signatures\": [\n          \"unsupported operand type\",\n          \"NoneType\"\n        ],\n        \"root_cause\": \"old Python runtime\",\n        \"solution_steps\": [\n          \"use Python 3.12\"\n        ],\n        \"commands\": [],\n        \"verification\": [],\n        \"applies_to\": [],\n        \"source\": \"user\",\n        \"confidence\": 0.8,\n        \"status\": \"approved\",\n        \"tags\": [],\n        \"times_used\": 0,\n        \"last_used_at\": null,\n        \"created_at\": \"2026-04-27T15:04:52.075926+00:00\",\n        \"updated_at\": \"2026-04-27T15:04:52.076015+00:00\",\n        \"deprecated_reason\": null,\n        \"reject_reason\": null\n      }\n    }\n  ],\n  \"index_doc_count\": 2\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "semantic-context",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo",
        "--task",
        "old python union type error"
      ],
      "returncode": 0,
      "stdout": "# Semantic Memory Search\n\n- [skill] Fix Python venv mismatch (id=SKILL-94f3940e0c9a, score=0.50884)\n  - signatures: unsupported operand type; NoneType\n  - solution: use Python 3.12\n\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "context",
        "--repo",
        "/mnt/data/uacos_phase14_cli_repo",
        "--task",
        "old python union type error"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"59ebc02a609c13742064bc2c\",\n  \"token_count\": 239,\n  \"content\": \"# UACOS Context Pack v0\\n\\n## Task\\nold python union type error\\n\\n## Relevant Memory\\nNo active project memories matched this task.\\n\\n## Relevant Skills\\n# Relevant Reusable Skills\\n\\n- [approved] Fix Python venv mismatch (id=SKILL-94f3940e0c9a, score=5.55, used=0)\\n  - signatures: unsupported operand type, NoneType\\n  - solution: use Python 3.12\\n\\n\\n## Semantic Memory Search\\n# Semantic Memory Search\\n\\n- [skill] Fix Python venv mismatch (id=SKILL-94f3940e0c9a, score=0.50884)\\n  - signatures: unsupported operand type; NoneType\\n  - solution: use Python 3.12\\n\\n\\n## Operating Rules\\n- Use this context instead of reading the whole repository.\\n- Do not access secret-like files such as `.env`, `*.pem`, `*.key`.\\n- Ask for scope expansion if more files are required.\\n- Do not claim DONE without tests or explicit validation evidence.\\n\\n## Repo Map\\n# Repo Map\\n\\nQuery: old python union type error\\n\\n## app.py\\n- L1-L2 `function` **ok** — def ok():\\n\\n\\n## Search Hits\\n\\n## Snippets\\n\"\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_16_TEST_REPORT.md`

# Phase 16 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_llm": true,
    "help_has_context_compress": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE16_SMOKE_OK\nllm= dry_run\nnew_file= True\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress} ...\n\nUniversal AI Context OS v2.1 - Phase 16 LLM Execution Layer\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress}\n\noptions:\n  -h, --help            show this help message and exit\n",
    "stderr": ""
  }
}
```

---

## Source: `PHASE_17_TEST_REPORT.md`

# Phase 17 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_skill_execute": true,
    "cli_all_ok": true,
    "cli_skill_id": true,
    "cli_done": true,
    "history_exists": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE17_SMOKE_OK\nskill= SKILL-c87c92b884c0\nexecutions= 3\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary} ...\n\nUniversal AI Context OS v2.2 - Phase 17 Skill Execution Engine\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-hi",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase17_cli_repo_fix"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase17_cli_repo_fix\",\n  \"db\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-27T23:48:18.060510+00:00\",\n    \"finished_at\": \"2026-04-27T23:48:18.062712+00:00\"\n  },\n  \"created_at\": \"2026-04-27T23:48:18.062754+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-add",
        "--repo",
        "/mnt/data/uacos_phase17_cli_repo_fix",
        "--title",
        "Verify Python value module",
        "--problem",
        "verify value module",
        "--solution",
        "run python assertion",
        "--command",
        "python -S -c \"import check_target; assert check_target.value()==42\"",
        "--status",
        "approved"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKILL-4e5622e9f302\",\n  \"title\": \"Verify Python value module\",\n  \"category\": \"general\",\n  \"problem_signatures\": [\n    \"verify value module\"\n  ],\n  \"root_cause\": \"\",\n  \"solution_steps\": [\n    \"run python assertion\"\n  ],\n  \"commands\": [\n    \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\"\n  ],\n  \"verification\": [],\n  \"applies_to\": [],\n  \"source\": \"user\",\n  \"confidence\": 0.8,\n  \"status\": \"approved\",\n  \"tags\": [],\n  \"times_used\": 0,\n  \"last_used_at\": null,\n  \"created_at\": \"2026-04-27T23:48:18.226814+00:00\",\n  \"updated_at\": \"2026-04-27T23:48:18.226846+00:00\",\n  \"deprecated_reason\": null,\n  \"reject_reason\": null\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-plan",
        "--repo",
        "/mnt/data/uacos_phase17_cli_repo_fix",
        "--skill-id",
        "SKILL-4e5622e9f302"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"skill_id\": \"SKILL-4e5622e9f302\",\n  \"title\": \"Verify Python value module\",\n  \"skill_status\": \"approved\",\n  \"task\": \"\",\n  \"dry_run\": true,\n  \"step_count\": 1,\n  \"blocked_count\": 0,\n  \"steps\": [\n    {\n      \"step\": 1,\n      \"command\": \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\",\n      \"safe\": true,\n      \"safety_reason\": \"allowed_prefix\",\n      \"would_run\": false\n    }\n  ],\n  \"created_at\": \"2026-04-27T23:48:18.382529+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-execute",
        "--repo",
        "/mnt/data/uacos_phase17_cli_repo_fix",
        "--skill-id",
        "SKILL-4e5622e9f302"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKEXEC-893b9be1e1f4\",\n  \"status\": \"dry_run\",\n  \"skill_id\": \"SKILL-4e5622e9f302\",\n  \"title\": \"Verify Python value module\",\n  \"task\": \"\",\n  \"dry_run\": true,\n  \"plan\": {\n    \"status\": \"ok\",\n    \"skill_id\": \"SKILL-4e5622e9f302\",\n    \"title\": \"Verify Python value module\",\n    \"skill_status\": \"approved\",\n    \"task\": \"\",\n    \"dry_run\": true,\n    \"step_count\": 1,\n    \"blocked_count\": 0,\n    \"steps\": [\n      {\n        \"step\": 1,\n        \"command\": \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\",\n        \"safe\": true,\n        \"safety_reason\": \"allowed_prefix\",\n        \"would_run\": false\n      }\n    ],\n    \"created_at\": \"2026-04-27T23:48:18.537518+00:00\"\n  },\n  \"results\": [],\n  \"created_at\": \"2026-04-27T23:48:18.537582+00:00\",\n  \"execution_file\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/skill_executions/SKEXEC-893b9be1e1f4.json\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-execute",
        "--repo",
        "/mnt/data/uacos_phase17_cli_repo_fix",
        "--skill-id",
        "SKILL-4e5622e9f302",
        "--yes-run"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKEXEC-5b6d6e5ec709\",\n  \"status\": \"done\",\n  \"skill_id\": \"SKILL-4e5622e9f302\",\n  \"title\": \"Verify Python value module\",\n  \"task\": \"\",\n  \"dry_run\": false,\n  \"plan\": {\n    \"status\": \"ok\",\n    \"skill_id\": \"SKILL-4e5622e9f302\",\n    \"title\": \"Verify Python value module\",\n    \"skill_status\": \"approved\",\n    \"task\": \"\",\n    \"dry_run\": false,\n    \"step_count\": 1,\n    \"blocked_count\": 0,\n    \"steps\": [\n      {\n        \"step\": 1,\n        \"command\": \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\",\n        \"safe\": true,\n        \"safety_reason\": \"allowed_prefix\",\n        \"would_run\": true\n      }\n    ],\n    \"created_at\": \"2026-04-27T23:48:18.680409+00:00\"\n  },\n  \"results\": [\n    {\n      \"command\": \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\",\n      \"returncode\": 0,\n      \"stdout\": \"\",\n      \"stderr\": \"\",\n      \"ok\": true\n    }\n  ],\n  \"created_at\": \"2026-04-27T23:48:18.680492+00:00\",\n  \"execution_file\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/skill_executions/SKEXEC-5b6d6e5ec709.json\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-exec-summary",
        "--repo",
        "/mnt/data/uacos_phase17_cli_repo_fix"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"count\": 2,\n  \"by_status\": {\n    \"dry_run\": 1,\n    \"done\": 1\n  },\n  \"recent\": [\n    {\n      \"id\": \"SKEXEC-893b9be1e1f4\",\n      \"skill_id\": \"SKILL-4e5622e9f302\",\n      \"title\": \"Verify Python value module\",\n      \"task\": \"\",\n      \"status\": \"dry_run\",\n      \"dry_run\": true,\n      \"created_at\": \"2026-04-27T23:48:18.537582+00:00\",\n      \"execution_file\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/skill_executions/SKEXEC-893b9be1e1f4.json\"\n    },\n    {\n      \"id\": \"SKEXEC-5b6d6e5ec709\",\n      \"skill_id\": \"SKILL-4e5622e9f302\",\n      \"title\": \"Verify Python value module\",\n      \"task\": \"\",\n      \"status\": \"done\",\n      \"dry_run\": false,\n      \"created_at\": \"2026-04-27T23:48:18.680492+00:00\",\n      \"execution_file\": \"/mnt/data/uacos_phase17_cli_repo_fix/.uacos/skill_executions/SKEXEC-5b6d6e5ec709.json\"\n    }\n  ]\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_18_TEST_REPORT.md`

# Phase 18 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_feedback": true,
    "cli_all_ok": true,
    "cli_skill_id": true,
    "feedback_scores_exists": true,
    "feedback_events_exists": true,
    "cli_recommend_has_skill": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE18_SMOKE_OK\nskill= SKILL-bfee5b488dd0\nreliability= 0.6667\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events} ...\n\nUniversal AI Context OS v2.3 - Phase 18 Learning Feedback Loop\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase18_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase18_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase18_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase18_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-27T23:55:30.954153+00:00\",\n    \"finished_at\": \"2026-04-27T23:55:30.956809+00:00\"\n  },\n  \"created_at\": \"2026-04-27T23:55:30.956859+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-add",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo",
        "--title",
        "Verify Python value module",
        "--problem",
        "verify value module",
        "--solution",
        "run python assertion",
        "--command",
        "python -S -c \"import check_target; assert check_target.value()==42\"",
        "--status",
        "approved"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKILL-f54ff5e0c357\",\n  \"title\": \"Verify Python value module\",\n  \"category\": \"general\",\n  \"problem_signatures\": [\n    \"verify value module\"\n  ],\n  \"root_cause\": \"\",\n  \"solution_steps\": [\n    \"run python assertion\"\n  ],\n  \"commands\": [\n    \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\"\n  ],\n  \"verification\": [],\n  \"applies_to\": [],\n  \"source\": \"user\",\n  \"confidence\": 0.8,\n  \"status\": \"approved\",\n  \"tags\": [],\n  \"times_used\": 0,\n  \"last_used_at\": null,\n  \"created_at\": \"2026-04-27T23:55:31.114605+00:00\",\n  \"updated_at\": \"2026-04-27T23:55:31.114633+00:00\",\n  \"deprecated_reason\": null,\n  \"reject_reason\": null\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "skill-execute",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo",
        "--skill-id",
        "SKILL-f54ff5e0c357",
        "--yes-run"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"SKEXEC-445e540aaa85\",\n  \"status\": \"done\",\n  \"skill_id\": \"SKILL-f54ff5e0c357\",\n  \"title\": \"Verify Python value module\",\n  \"task\": \"\",\n  \"dry_run\": false,\n  \"plan\": {\n    \"status\": \"ok\",\n    \"skill_id\": \"SKILL-f54ff5e0c357\",\n    \"title\": \"Verify Python value module\",\n    \"skill_status\": \"approved\",\n    \"task\": \"\",\n    \"dry_run\": false,\n    \"step_count\": 1,\n    \"blocked_count\": 0,\n    \"steps\": [\n      {\n        \"step\": 1,\n        \"command\": \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\",\n        \"safe\": true,\n        \"safety_reason\": \"allowed_prefix\",\n        \"would_run\": true\n      }\n    ],\n    \"created_at\": \"2026-04-27T23:55:31.316380+00:00\"\n  },\n  \"results\": [\n    {\n      \"command\": \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\",\n      \"returncode\": 0,\n      \"stdout\": \"\",\n      \"stderr\": \"\",\n      \"ok\": true\n    }\n  ],\n  \"created_at\": \"2026-04-27T23:55:31.316443+00:00\",\n  \"execution_file\": \"/mnt/data/uacos_phase18_cli_repo/.uacos/skill_executions/SKEXEC-445e540aaa85.json\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "feedback-ingest-execution",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo",
        "--all"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"ingested\": 1,\n  \"results\": [\n    {\n      \"status\": \"ok\",\n      \"skill_id\": \"SKILL-f54ff5e0c357\",\n      \"score\": {\n        \"skill_id\": \"SKILL-f54ff5e0c357\",\n        \"success_count\": 1,\n        \"failure_count\": 0,\n        \"blocked_count\": 0,\n        \"dry_run_count\": 0,\n        \"last_status\": \"done\",\n        \"last_event_at\": \"2026-04-27T23:55:31.512818+00:00\",\n        \"reliability\": 0.6667,\n        \"confidence_delta\": 0.03,\n        \"activity\": 1\n      },\n      \"event\": {\n        \"event\": \"ingest_skill_execution\",\n        \"skill_id\": \"SKILL-f54ff5e0c357\",\n        \"execution_id\": \"SKEXEC-445e540aaa85\",\n        \"execution_status\": \"done\",\n        \"score\": {\n          \"skill_id\": \"SKILL-f54ff5e0c357\",\n          \"success_count\": 1,\n          \"failure_count\": 0,\n          \"blocked_count\": 0,\n          \"dry_run_count\": 0,\n          \"last_status\": \"done\",\n          \"last_event_at\": \"2026-04-27T23:55:31.512818+00:00\",\n          \"reliability\": 0.6667,\n          \"confidence_delta\": 0.03,\n          \"activity\": 1\n        },\n        \"ts\": \"2026-04-27T23:55:31.513023+00:00\"\n      }\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "feedback-skill-score",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo",
        "--skill-id",
        "SKILL-f54ff5e0c357"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"skill\": {\n    \"id\": \"SKILL-f54ff5e0c357\",\n    \"title\": \"Verify Python value module\",\n    \"category\": \"general\",\n    \"problem_signatures\": [\n      \"verify value module\"\n    ],\n    \"root_cause\": \"\",\n    \"solution_steps\": [\n      \"run python assertion\"\n    ],\n    \"commands\": [\n      \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\"\n    ],\n    \"verification\": [],\n    \"applies_to\": [],\n    \"source\": \"user\",\n    \"confidence\": 0.8,\n    \"status\": \"approved\",\n    \"tags\": [],\n    \"times_used\": 1,\n    \"last_used_at\": \"2026-04-27T23:55:31.354251+00:00\",\n    \"created_at\": \"2026-04-27T23:55:31.114605+00:00\",\n    \"updated_at\": \"2026-04-27T23:55:31.354251+00:00\",\n    \"deprecated_reason\": null,\n    \"reject_reason\": null\n  },\n  \"score\": {\n    \"skill_id\": \"SKILL-f54ff5e0c357\",\n    \"success_count\": 1,\n    \"failure_count\": 0,\n    \"blocked_count\": 0,\n    \"dry_run_count\": 0,\n    \"last_status\": \"done\",\n    \"last_event_at\": \"2026-04-27T23:55:31.512818+00:00\",\n    \"reliability\": 0.6667,\n    \"confidence_delta\": 0.03,\n    \"activity\": 1\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "feedback-recommend",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo",
        "--task",
        "verify value module python check"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"verify value module python check\",\n  \"recommendations\": [\n    {\n      \"id\": \"SKILL-f54ff5e0c357\",\n      \"title\": \"Verify Python value module\",\n      \"category\": \"general\",\n      \"problem_signatures\": [\n        \"verify value module\"\n      ],\n      \"root_cause\": \"\",\n      \"solution_steps\": [\n        \"run python assertion\"\n      ],\n      \"commands\": [\n        \"python -S -c \\\"import check_target; assert check_target.value()==42\\\"\"\n      ],\n      \"verification\": [],\n      \"applies_to\": [],\n      \"source\": \"user\",\n      \"confidence\": 0.8,\n      \"status\": \"approved\",\n      \"tags\": [],\n      \"times_used\": 1,\n      \"last_used_at\": \"2026-04-27T23:55:31.354251+00:00\",\n      \"created_at\": \"2026-04-27T23:55:31.114605+00:00\",\n      \"updated_at\": \"2026-04-27T23:55:31.354251+00:00\",\n      \"deprecated_reason\": null,\n      \"reject_reason\": null,\n      \"_score\": 9.1,\n      \"feedback\": {\n        \"skill_id\": \"SKILL-f54ff5e0c357\",\n        \"success_count\": 1,\n        \"failure_count\": 0,\n        \"blocked_count\": 0,\n        \"dry_run_count\": 0,\n        \"last_status\": \"done\",\n        \"last_event_at\": \"2026-04-27T23:55:31.512818+00:00\",\n        \"reliability\": 0.6667,\n        \"confidence_delta\": 0.03,\n        \"activity\": 1\n      },\n      \"recommendation_score\": 9.8167\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "feedback-summary",
        "--repo",
        "/mnt/data/uacos_phase18_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"feedback_events\": 1,\n  \"tracked_skills\": 1,\n  \"by_last_status\": {\n    \"done\": 1\n  },\n  \"top_skills\": [\n    {\n      \"skill_id\": \"SKILL-f54ff5e0c357\",\n      \"success_count\": 1,\n      \"failure_count\": 0,\n      \"blocked_count\": 0,\n      \"dry_run_count\": 0,\n      \"last_status\": \"done\",\n      \"last_event_at\": \"2026-04-27T23:55:31.512818+00:00\",\n      \"reliability\": 0.6667,\n      \"confidence_delta\": 0.03,\n      \"activity\": 1\n    }\n  ],\n  \"recent_events\": [\n    {\n      \"event\": \"ingest_skill_execution\",\n      \"skill_id\": \"SKILL-f54ff5e0c357\",\n      \"execution_id\": \"SKEXEC-445e540aaa85\",\n      \"execution_status\": \"done\",\n      \"score\": {\n        \"skill_id\": \"SKILL-f54ff5e0c357\",\n        \"success_count\": 1,\n        \"failure_count\": 0,\n        \"blocked_count\": 0,\n        \"dry_run_count\": 0,\n        \"last_status\": \"done\",\n        \"last_event_at\": \"2026-04-27T23:55:31.512818+00:00\",\n        \"reliability\": 0.6667,\n        \"confidence_delta\": 0.03,\n        \"activity\": 1\n      },\n      \"ts\": \"2026-04-27T23:55:31.513023+00:00\"\n    }\n  ]\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_19_TEST_REPORT.md`

# Phase 19 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_ast": true,
    "help_has_context_smart": true,
    "cli_all_ok": true,
    "graph_file_exists": true,
    "smart_context_exists": true,
    "cli_context_mentions_db": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE19_SMOKE_OK\nfiles= 3\ncalls= 4\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart} ...\n\nUniversal AI Context OS v2.4 - Phase 19 AST Dependency Graph Engine\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autop",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase19_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase19_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase19_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase19_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase19_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 3,\n    \"files_indexed\": 3,\n    \"files_skipped\": 0,\n    \"files_changed\": 3,\n    \"symbols_indexed\": 4,\n    \"started_at\": \"2026-04-28T00:24:04.216142+00:00\",\n    \"finished_at\": \"2026-04-28T00:24:04.219222+00:00\"\n  },\n  \"created_at\": \"2026-04-28T00:24:04.219267+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "ast-scan",
        "--repo",
        "/mnt/data/uacos_phase19_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"graph_dir\": \"/mnt/data/uacos_phase19_cli_repo/.uacos/graph\",\n  \"stats\": {\n    \"file_count\": 3,\n    \"file_edge_count\": 2,\n    \"call_edge_count\": 4,\n    \"symbol_count\": 4,\n    \"parse_errors\": 0\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "graph-query",
        "--repo",
        "/mnt/data/uacos_phase19_cli_repo",
        "--symbol",
        "create_user"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"query\": \"create_user\",\n  \"matches\": [\n    {\n      \"symbol\": \"create_user\",\n      \"file\": \"service.py\"\n    }\n  ],\n  \"calls_from\": [\n    {\n      \"source_file\": \"service.py\",\n      \"caller\": \"create_user\",\n      \"callee\": \"validate_user\",\n      \"target_file\": \"service.py\",\n      \"lineno\": 7\n    },\n    {\n      \"source_file\": \"service.py\",\n      \"caller\": \"create_user\",\n      \"callee\": \"save_user\",\n      \"target_file\": \"db.py\",\n      \"lineno\": 8\n    }\n  ],\n  \"calls_to\": [\n    {\n      \"source_file\": \"router.py\",\n      \"caller\": \"route_create\",\n      \"callee\": \"create_user\",\n      \"target_file\": \"service.py\",\n      \"lineno\": 4\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "impact",
        "--repo",
        "/mnt/data/uacos_phase19_cli_repo",
        "--task",
        "fix db save_user error"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"fix db save_user error\",\n  \"impacted_files\": [\n    {\n      \"file\": \"db.py\",\n      \"score\": 1.5,\n      \"reasons\": [\n        \"symbol:save_user\"\n      ]\n    },\n    {\n      \"file\": \"service.py\",\n      \"score\": 1.25,\n      \"reasons\": [\n        \"symbol:save_user\"\n      ]\n    },\n    {\n      \"file\": \"router.py\",\n      \"score\": 1.0,\n      \"reasons\": [\n        \"symbol:save_user\"\n      ]\n    }\n  ],\n  \"token_count\": 4\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "context-smart",
        "--repo",
        "/mnt/data/uacos_phase19_cli_repo",
        "--task",
        "fix db save_user error"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"fix db save_user error\",\n  \"included_files\": [\n    \"db.py\",\n    \"service.py\",\n    \"router.py\"\n  ],\n  \"impact\": {\n    \"status\": \"ok\",\n    \"task\": \"fix db save_user error\",\n    \"impacted_files\": [\n      {\n        \"file\": \"db.py\",\n        \"score\": 1.5,\n        \"reasons\": [\n          \"symbol:save_user\"\n        ]\n      },\n      {\n        \"file\": \"service.py\",\n        \"score\": 1.25,\n        \"reasons\": [\n          \"symbol:save_user\"\n        ]\n      },\n      {\n        \"file\": \"router.py\",\n        \"score\": 1.0,\n        \"reasons\": [\n          \"symbol:save_user\"\n        ]\n      }\n    ],\n    \"token_count\": 4\n  },\n  \"context_file\": \"/mnt/data/uacos_phase19_cli_repo/.uacos/smart_context/latest_smart_context.md\",\n  \"char_count\": 611\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_20_TEST_REPORT.md`

# Phase 20 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_patch20": true,
    "cli_all_ok": true,
    "cli_new_file_exists": true,
    "cli_modify_applied": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE20_SMOKE_OK\nfiles= 4\nstatus= applied\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback} ...\n\nUniversal AI Context OS v2.5 - Phase 20 Production Patch Engine\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-searc",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "patch20-parse",
        "--patch",
        "/mnt/data/uacos_phase20_cli_repo/change.diff"
      ],
      "returncode": 0,
      "stdout": "{\n  \"files\": [\n    {\n      \"old_path\": \"app.py\",\n      \"new_path\": \"app.py\",\n      \"operation\": \"modify\",\n      \"headers\": [\n        \"diff --git a/app.py b/app.py\",\n        \"--- a/app.py\",\n        \"+++ b/app.py\"\n      ],\n      \"hunks\": [\n        {\n          \"header\": \"@@ -1,2 +1,2 @@\",\n          \"lines\": [\n            \" def value():\",\n            \"-    return 1\",\n            \"+    return 42\"\n          ]\n        }\n      ],\n      \"raw_lines\": [\n        \"diff --git a/app.py b/app.py\",\n        \"--- a/app.py\",\n        \"+++ b/app.py\",\n        \"@@ -1,2 +1,2 @@\",\n        \" def value():\",\n        \"-    return 1\",\n        \"+    return 42\"\n      ],\n      \"path\": \"app.py\"\n    },\n    {\n      \"old_path\": \"newmod.py\",\n      \"new_path\": \"newmod.py\",\n      \"operation\": \"new\",\n      \"headers\": [\n        \"diff --git a/newmod.py b/newmod.py\",\n        \"--- /dev/null\",\n        \"+++ b/newmod.py\"\n      ],\n      \"hunks\": [\n        {\n          \"header\": \"@@ -0,0 +1,2 @@\",\n          \"lines\": [\n            \"+def answer():\",\n            \"+    return 42\"\n          ]\n        }\n      ],\n      \"raw_lines\": [\n        \"diff --git a/newmod.py b/newmod.py\",\n        \"new file mode 100644\",\n        \"--- /dev/null\",\n        \"+++ b/newmod.py\",\n        \"@@ -0,0 +1,2 @@\",\n        \"+def answer():\",\n        \"+    return 42\"\n      ],\n      \"path\": \"newmod.py\"\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "patch20-validate",
        "--repo",
        "/mnt/data/uacos_phase20_cli_repo",
        "--patch",
        "/mnt/data/uacos_phase20_cli_repo/change.diff",
        "--allowed-file",
        "app.py",
        "--allowed-file",
        "newmod.py"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"pass\",\n  \"file_count\": 2,\n  \"files\": [\n    {\n      \"old_path\": \"app.py\",\n      \"new_path\": \"app.py\",\n      \"operation\": \"modify\",\n      \"headers\": [\n        \"diff --git a/app.py b/app.py\",\n        \"--- a/app.py\",\n        \"+++ b/app.py\"\n      ],\n      \"hunks\": [\n        {\n          \"header\": \"@@ -1,2 +1,2 @@\",\n          \"lines\": [\n            \" def value():\",\n            \"-    return 1\",\n            \"+    return 42\"\n          ]\n        }\n      ],\n      \"path\": \"app.py\"\n    },\n    {\n      \"old_path\": \"newmod.py\",\n      \"new_path\": \"newmod.py\",\n      \"operation\": \"new\",\n      \"headers\": [\n        \"diff --git a/newmod.py b/newmod.py\",\n        \"--- /dev/null\",\n        \"+++ b/newmod.py\"\n      ],\n      \"hunks\": [\n        {\n          \"header\": \"@@ -0,0 +1,2 @@\",\n          \"lines\": [\n            \"+def answer():\",\n            \"+    return 42\"\n          ]\n        }\n      ],\n      \"path\": \"newmod.py\"\n    }\n  ],\n  \"findings\": []\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "patch20-apply",
        "--repo",
        "/mnt/data/uacos_phase20_cli_repo",
        "--patch",
        "/mnt/data/uacos_phase20_cli_repo/change.diff",
        "--allowed-file",
        "app.py",
        "--allowed-file",
        "newmod.py",
        "--dry-run"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"PATCH-fa973be14cf9\",\n  \"status\": \"planned\",\n  \"patch_file\": \"/mnt/data/uacos_phase20_cli_repo/change.diff\",\n  \"validation\": {\n    \"status\": \"pass\",\n    \"file_count\": 2,\n    \"files\": [\n      {\n        \"old_path\": \"app.py\",\n        \"new_path\": \"app.py\",\n        \"operation\": \"modify\",\n        \"headers\": [\n          \"diff --git a/app.py b/app.py\",\n          \"--- a/app.py\",\n          \"+++ b/app.py\"\n        ],\n        \"hunks\": [\n          {\n            \"header\": \"@@ -1,2 +1,2 @@\",\n            \"lines\": [\n              \" def value():\",\n              \"-    return 1\",\n              \"+    return 42\"\n            ]\n          }\n        ],\n        \"path\": \"app.py\"\n      },\n      {\n        \"old_path\": \"newmod.py\",\n        \"new_path\": \"newmod.py\",\n        \"operation\": \"new\",\n        \"headers\": [\n          \"diff --git a/newmod.py b/newmod.py\",\n          \"--- /dev/null\",\n          \"+++ b/newmod.py\"\n        ],\n        \"hunks\": [\n          {\n            \"header\": \"@@ -0,0 +1,2 @@\",\n            \"lines\": [\n              \"+def answer():\",\n              \"+    return 42\"\n            ]\n          }\n        ],\n        \"path\": \"newmod.py\"\n      }\n    ],\n    \"findings\": []\n  },\n  \"dry_run\": true,\n  \"changed\": [],\n  \"tests\": [],\n  \"created_at\": \"2026-04-28T00:29:47.403630+00:00\",\n  \"run_dir\": \"/mnt/data/uacos_phase20_cli_repo/.uacos/patch_runs/PATCH-fa973be14cf9\",\n  \"manifest_file\": \"/mnt/data/uacos_phase20_cli_repo/.uacos/patch_runs/PATCH-fa973be14cf9/manifest.json\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "patch20-apply",
        "--repo",
        "/mnt/data/uacos_phase20_cli_repo",
        "--patch",
        "/mnt/data/uacos_phase20_cli_repo/change.diff",
        "--allowed-file",
        "app.py",
        "--allowed-file",
        "newmod.py",
        "--test",
        "python -S -c \"import app, newmod; assert app.value()==42 and newmod.answer()==42\""
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"PATCH-e2086f32d0d2\",\n  \"status\": \"applied\",\n  \"patch_file\": \"/mnt/data/uacos_phase20_cli_repo/change.diff\",\n  \"validation\": {\n    \"status\": \"pass\",\n    \"file_count\": 2,\n    \"files\": [\n      {\n        \"old_path\": \"app.py\",\n        \"new_path\": \"app.py\",\n        \"operation\": \"modify\",\n        \"headers\": [\n          \"diff --git a/app.py b/app.py\",\n          \"--- a/app.py\",\n          \"+++ b/app.py\"\n        ],\n        \"hunks\": [\n          {\n            \"header\": \"@@ -1,2 +1,2 @@\",\n            \"lines\": [\n              \" def value():\",\n              \"-    return 1\",\n              \"+    return 42\"\n            ]\n          }\n        ],\n        \"path\": \"app.py\"\n      },\n      {\n        \"old_path\": \"newmod.py\",\n        \"new_path\": \"newmod.py\",\n        \"operation\": \"new\",\n        \"headers\": [\n          \"diff --git a/newmod.py b/newmod.py\",\n          \"--- /dev/null\",\n          \"+++ b/newmod.py\"\n        ],\n        \"hunks\": [\n          {\n            \"header\": \"@@ -0,0 +1,2 @@\",\n            \"lines\": [\n              \"+def answer():\",\n              \"+    return 42\"\n            ]\n          }\n        ],\n        \"path\": \"newmod.py\"\n      }\n    ],\n    \"findings\": []\n  },\n  \"dry_run\": false,\n  \"changed\": [\n    {\n      \"operation\": \"modify\",\n      \"path\": \"app.py\",\n      \"backup\": \"/mnt/data/uacos_phase20_cli_repo/.uacos/patch_runs/PATCH-e2086f32d0d2/backup/app.py\",\n      \"notes\": []\n    },\n    {\n      \"operation\": \"new\",\n      \"path\": \"newmod.py\"\n    }\n  ],\n  \"tests\": [\n    {\n      \"command\": \"python -S -c \\\"import app, newmod; assert app.value()==42 and newmod.answer()==42\\\"\",\n      \"returncode\": 0,\n      \"stdout\": \"\",\n      \"stderr\": \"\",\n      \"ok\": true\n    }\n  ],\n  \"created_at\": \"2026-04-28T00:29:47.546808+00:00\",\n  \"run_dir\": \"/mnt/data/uacos_phase20_cli_repo/.uacos/patch_runs/PATCH-e2086f32d0d2\",\n  \"manifest_file\": \"/mnt/data/uacos_phase20_cli_repo/.uacos/patch_runs/PATCH-e2086f32d0d2/manifest.json\"\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_21_TEST_REPORT.md`

# Phase 21 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_provider_health": true,
    "cli_all_ok": true,
    "history_exists": true,
    "secret_redacted": true,
    "route_cli_ok": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE21_SMOKE_OK\nroute= coding\nruns= 1\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test} ...\n\nUniversal AI Context OS v2.6 - Phase 21 Provider Hardening\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase21_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase21_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase21_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase21_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 0,\n    \"files_indexed\": 0,\n    \"files_skipped\": 0,\n    \"files_changed\": 0,\n    \"symbols_indexed\": 0,\n    \"started_at\": \"2026-04-28T00:37:12.661779+00:00\",\n    \"finished_at\": \"2026-04-28T00:37:12.663411+00:00\"\n  },\n  \"created_at\": \"2026-04-28T00:37:12.663463+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "llm-init",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"config\": \"/mnt/data/uacos_phase21_cli_repo/.uacos/llm_providers.json\",\n  \"config_data\": {\n    \"version\": 1,\n    \"default_provider\": \"dry_run\",\n    \"providers\": {\n      \"dry_run\": {\n        \"type\": \"dry_run\",\n        \"model\": \"dry-run\",\n        \"enabled\": true\n      },\n      \"ollama\": {\n        \"type\": \"ollama\",\n        \"base_url\": \"http://127.0.0.1:11434\",\n        \"model\": \"qwen2.5-coder:7b\",\n        \"enabled\": false,\n        \"timeout_sec\": 120\n      },\n      \"openai_compatible\": {\n        \"type\": \"openai_compatible\",\n        \"base_url\": \"http://127.0.0.1:3000/v1\",\n        \"model\": \"local-model\",\n        \"api_key_env\": \"UACOS_OPENAI_API_KEY\",\n        \"enabled\": false,\n        \"timeout_sec\": 120\n      }\n    },\n    \"safety\": {\n      \"dry_run_default\": true,\n      \"require_provider_enabled\": true,\n      \"max_prompt_chars\": 120000\n    }\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "provider-health",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"provider\": \"dry_run\",\n  \"type\": \"dry_run\",\n  \"mode\": \"dry_run\",\n  \"checked_at\": \"2026-04-28T00:37:13.082015+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "model-route-set",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo",
        "--name",
        "coding",
        "--provider",
        "dry_run",
        "--model",
        "dry-run",
        "--keyword",
        "code",
        "--keyword",
        "bug"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"route\": \"coding\",\n  \"config\": {\n    \"provider\": \"dry_run\",\n    \"model\": \"dry-run\",\n    \"task_keywords\": [\n      \"code\",\n      \"bug\"\n    ],\n    \"updated_at\": \"2026-04-28T00:37:13.253874+00:00\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "model-route-test",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo",
        "--task",
        "fix code bug"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"route\": \"coding\",\n  \"provider\": \"dry_run\",\n  \"model\": \"dry-run\",\n  \"reason\": \"keyword:code\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "llm-run-hardened",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo",
        "--task",
        "fix code bug",
        "--prompt",
        "hello token=SECRET_VALUE",
        "--dry-run"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"dry_run\",\n  \"provider\": \"dry_run\",\n  \"model\": \"dry-run\",\n  \"route\": {\n    \"status\": \"ok\",\n    \"route\": \"coding\",\n    \"provider\": \"dry_run\",\n    \"model\": \"dry-run\",\n    \"reason\": \"keyword:code\"\n  },\n  \"attempts\": [\n    {\n      \"attempt\": 1,\n      \"status\": \"dry_run\"\n    }\n  ],\n  \"elapsed_sec\": 0.0002,\n  \"input_tokens_est\": 6,\n  \"output_tokens_est\": 18,\n  \"estimated_cost\": {\n    \"model\": \"dry-run\",\n    \"input_tokens\": 6,\n    \"output_tokens\": 18,\n    \"estimated_cost_usd\": 0.0,\n    \"pricing\": {\n      \"input_per_1k\": 0.0,\n      \"output_per_1k\": 0.0\n    }\n  },\n  \"result\": {\n    \"status\": \"dry_run\",\n    \"provider\": \"dry_run\",\n    \"model\": \"dry-run\",\n    \"prompt_chars\": 24,\n    \"content\": \"DRY_RUN: provider not called. Review prompt and enable provider when ready.\",\n    \"created_at\": \"2026-04-28T00:37:13.634414+00:00\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "provider-summary",
        "--repo",
        "/mnt/data/uacos_phase21_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"runs\": 1,\n  \"by_provider\": {\n    \"dry_run\": {\n      \"runs\": 1,\n      \"statuses\": {\n        \"dry_run\": 1\n      },\n      \"estimated_cost_usd\": 0.0\n    }\n  },\n  \"estimated_cost_usd\": 0.0,\n  \"recent\": [\n    {\n      \"event\": \"llm_run\",\n      \"provider\": \"dry_run\",\n      \"model\": \"dry-run\",\n      \"route\": {\n        \"status\": \"ok\",\n        \"route\": \"coding\",\n        \"provider\": \"dry_run\",\n        \"model\": \"dry-run\",\n        \"reason\": \"keyword:code\"\n      },\n      \"status\": \"dry_run\",\n      \"attempts\": [\n        {\n          \"attempt\": 1,\n          \"status\": \"dry_run\"\n        }\n      ],\n      \"elapsed_sec\": 0.0002,\n      \"input_tokens_est\": 6,\n      \"output_tokens_est\": 18,\n      \"estimated_cost\": {\n        \"model\": \"dry-run\",\n        \"input_tokens\": 6,\n        \"output_tokens\": 18,\n        \"estimated_cost_usd\": 0.0,\n        \"pricing\": {\n          \"input_per_1k\": 0.0,\n          \"output_per_1k\": 0.0\n        }\n      },\n      \"prompt\": \"hello token=***REDACTED***\",\n      \"response\": \"DRY_RUN: provider not called. Review prompt and enable provider when ready.\",\n      \"ts\": \"2026-04-28T00:37:13.634479+00:00\"\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "token-estimate",
        "--text",
        "hello world",
        "--model",
        "dry-run"
      ],
      "returncode": 0,
      "stdout": "{\n  \"tokens_est\": 2,\n  \"chars\": 11,\n  \"cost\": {\n    \"model\": \"dry-run\",\n    \"input_tokens\": 2,\n    \"output_tokens\": 0,\n    \"estimated_cost_usd\": 0.0,\n    \"pricing\": {\n      \"input_per_1k\": 0.0,\n      \"output_per_1k\": 0.0\n    }\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "redact-test",
        "--text",
        "api_key=SECRET_VALUE"
      ],
      "returncode": 0,
      "stdout": "{\n  \"redacted\": \"api_key=***REDACTED***\"\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_22_TEST_REPORT.md`

# Phase 22 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_context_budget": true,
    "cli_all_ok": true,
    "cache_exists": true,
    "context_exists": true,
    "report_exists": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE22_SMOKE_OK\nprofile= small\nfiles= 2\ntokens= 151\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report} ...\n\nUniversal AI Context OS v2.7 - Phase 22 Context Budget Optimizer\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase22_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase22_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase22_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase22_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase22_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 2,\n    \"files_indexed\": 2,\n    \"files_skipped\": 0,\n    \"files_changed\": 2,\n    \"symbols_indexed\": 2,\n    \"started_at\": \"2026-04-28T00:43:04.945965+00:00\",\n    \"finished_at\": \"2026-04-28T00:43:04.949194+00:00\"\n  },\n  \"created_at\": \"2026-04-28T00:43:04.949245+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "memory-add",
        "--repo",
        "/mnt/data/uacos_phase22_cli_repo",
        "--kind",
        "project_truth",
        "--key",
        "user_flow",
        "--value",
        "create_user calls save_user in db.py"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"MEM-40d478610000\",\n  \"kind\": \"project_truth\",\n  \"key\": \"user_flow\",\n  \"value\": \"create_user calls save_user in db.py\",\n  \"source\": \"user\",\n  \"confidence\": 1.0,\n  \"tags\": [],\n  \"applies_to\": [],\n  \"valid_at\": \"2026-04-28T00:43:05.128686+00:00\",\n  \"invalid_at\": null,\n  \"invalid_reason\": null,\n  \"created_at\": \"2026-04-28T00:43:05.128718+00:00\",\n  \"updated_at\": \"2026-04-28T00:43:05.128720+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "budget-classify",
        "--task",
        "fix db save_user error"
      ],
      "returncode": 0,
      "stdout": "{\n  \"size\": \"small\",\n  \"reason\": \"heuristic_score:1\",\n  \"word_count\": 4\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "summary-cache",
        "--repo",
        "/mnt/data/uacos_phase22_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"updated\": 2,\n  \"skipped\": 0,\n  \"file_count\": 2,\n  \"cache_file\": \"/mnt/data/uacos_phase22_cli_repo/.uacos/budget/file_summary_cache.json\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "context-budget",
        "--repo",
        "/mnt/data/uacos_phase22_cli_repo",
        "--task",
        "fix db save_user error",
        "--profile",
        "small"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"fix db save_user error\",\n  \"profile\": \"small\",\n  \"task_class\": {\n    \"size\": \"small\",\n    \"reason\": \"heuristic_score:1\",\n    \"word_count\": 4\n  },\n  \"budget\": {\n    \"max_tokens\": 4500,\n    \"max_files\": 5,\n    \"per_file_tokens\": 850,\n    \"memory_tokens\": 500,\n    \"skill_tokens\": 500\n  },\n  \"selected_files\": [\n    {\n      \"file\": \"db.py\",\n      \"score\": 1.95,\n      \"tokens_est\": 31,\n      \"reasons\": [\n        \"impact\"\n      ]\n    },\n    {\n      \"file\": \"service.py\",\n      \"score\": 1.625,\n      \"tokens_est\": 43,\n      \"reasons\": [\n        \"impact\"\n      ]\n    }\n  ],\n  \"selected_file_count\": 2,\n  \"skills_count\": 0,\n  \"memories_count\": 1,\n  \"tokens_est\": 128,\n  \"context_file\": \"/mnt/data/uacos_phase22_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n  \"created_at\": \"2026-04-28T00:43:05.646165+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "budget-report",
        "--repo",
        "/mnt/data/uacos_phase22_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"fix db save_user error\",\n  \"profile\": \"small\",\n  \"task_class\": {\n    \"size\": \"small\",\n    \"reason\": \"heuristic_score:1\",\n    \"word_count\": 4\n  },\n  \"budget\": {\n    \"max_tokens\": 4500,\n    \"max_files\": 5,\n    \"per_file_tokens\": 850,\n    \"memory_tokens\": 500,\n    \"skill_tokens\": 500\n  },\n  \"selected_files\": [\n    {\n      \"file\": \"db.py\",\n      \"score\": 1.95,\n      \"tokens_est\": 31,\n      \"reasons\": [\n        \"impact\"\n      ]\n    },\n    {\n      \"file\": \"service.py\",\n      \"score\": 1.625,\n      \"tokens_est\": 43,\n      \"reasons\": [\n        \"impact\"\n      ]\n    }\n  ],\n  \"selected_file_count\": 2,\n  \"skills_count\": 0,\n  \"memories_count\": 1,\n  \"tokens_est\": 128,\n  \"context_file\": \"/mnt/data/uacos_phase22_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n  \"created_at\": \"2026-04-28T00:43:05.646165+00:00\"\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_23_TEST_REPORT.md`

# Phase 23 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_vscode_pro": true,
    "cli_all_ok": true,
    "extension_files_exist": true,
    "node_check_ok": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE23_SMOKE_OK\ncommands= 14\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check} ...\n\nUniversal AI Context OS v2.8 - Phase 23 VSCode Production Layer\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "vscode-pro-init",
        "--output-dir",
        "/mnt/data/uacos_phase23_vscode_extension_test",
        "--overwrite"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"output_dir\": \"/mnt/data/uacos_phase23_vscode_extension_test\",\n  \"files\": [\n    \"/mnt/data/uacos_phase23_vscode_extension_test/package.json\",\n    \"/mnt/data/uacos_phase23_vscode_extension_test/extension.js\",\n    \"/mnt/data/uacos_phase23_vscode_extension_test/README.md\",\n    \"/mnt/data/uacos_phase23_vscode_extension_test/scripts/check-extension.js\",\n    \"/mnt/data/uacos_phase23_vscode_extension_test/.vscode/launch.json\"\n  ],\n  \"created_at\": \"2026-04-28T00:50:34.315745+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "vscode-pro-check",
        "--output-dir",
        "/mnt/data/uacos_phase23_vscode_extension_test"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"pass\",\n  \"findings\": [],\n  \"output_dir\": \"/mnt/data/uacos_phase23_vscode_extension_test\"\n}\n",
      "stderr": ""
    }
  ],
  "node_cli": {
    "returncode": 0,
    "stdout": "EXTENSION_CHECK_OK\n",
    "stderr": ""
  }
}
```

---

## Source: `PHASE_24_TEST_REPORT.md`

# Phase 24 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_openclaw": true,
    "cli_all_ok": true,
    "prompt_exists": true,
    "history_exists": true,
    "dry_run_recorded": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE24_SMOKE_OK\nprompt_chars= 631\nruns= 1\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary} ...\n\nUniversal AI Context OS v2.9 - Phase 24 OpenClaw Adapter Production Layer\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase24_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-28T01:01:05.560483+00:00\",\n    \"finished_at\": \"2026-04-28T01:01:05.562912+00:00\"\n  },\n  \"created_at\": \"2026-04-28T01:01:05.562950+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "openclaw-init",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"config\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/openclaw/openclaw_adapter.json\",\n  \"config_data\": {\n    \"version\": 1,\n    \"command\": \"openclaw\",\n    \"chat_script\": \"\",\n    \"default_agent\": \"leader\",\n    \"mode\": \"dry_run\",\n    \"timeout_sec\": 300,\n    \"context_mode\": \"budget\",\n    \"context_profile\": \"medium\",\n    \"max_prompt_chars\": 120000,\n    \"output_file\": \"agent_response.md\",\n    \"allowed_real_run\": false,\n    \"notes\": \"Use dry_run until command path/agent are validated.\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "openclaw-validate",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"pass\",\n  \"findings\": [\n    {\n      \"severity\": \"warning\",\n      \"reason\": \"openclaw_command_not_found\",\n      \"command\": \"openclaw\"\n    }\n  ],\n  \"config\": {\n    \"version\": 1,\n    \"command\": \"openclaw\",\n    \"chat_script\": \"\",\n    \"default_agent\": \"leader\",\n    \"mode\": \"dry_run\",\n    \"timeout_sec\": 300,\n    \"context_mode\": \"budget\",\n    \"context_profile\": \"medium\",\n    \"max_prompt_chars\": 120000,\n    \"output_file\": \"agent_response.md\",\n    \"allowed_real_run\": false,\n    \"notes\": \"Use dry_run until command path/agent are validated.\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "openclaw-health",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"mode\": \"dry_run\",\n  \"validation\": {\n    \"status\": \"pass\",\n    \"findings\": [\n      {\n        \"severity\": \"warning\",\n        \"reason\": \"openclaw_command_not_found\",\n        \"command\": \"openclaw\"\n      }\n    ],\n    \"config\": {\n      \"version\": 1,\n      \"command\": \"openclaw\",\n      \"chat_script\": \"\",\n      \"default_agent\": \"leader\",\n      \"mode\": \"dry_run\",\n      \"timeout_sec\": 300,\n      \"context_mode\": \"budget\",\n      \"context_profile\": \"medium\",\n      \"max_prompt_chars\": 120000,\n      \"output_file\": \"agent_response.md\",\n      \"allowed_real_run\": false,\n      \"notes\": \"Use dry_run until command path/agent are validated.\"\n    }\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "openclaw-prompt",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo",
        "--task",
        "fix ok function",
        "--agent",
        "leader"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"agent\": \"leader\",\n  \"prompt_file\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/openclaw/latest_openclaw_prompt.md\",\n  \"prompt_chars\": 642,\n  \"context_mode\": \"budget\",\n  \"context_meta\": {\n    \"status\": \"ok\",\n    \"task\": \"fix ok function\",\n    \"profile\": \"medium\",\n    \"task_class\": {\n      \"size\": \"small\",\n      \"reason\": \"heuristic_score:1\",\n      \"word_count\": 3\n    },\n    \"budget\": {\n      \"max_tokens\": 8000,\n      \"max_files\": 8,\n      \"per_file_tokens\": 1000,\n      \"memory_tokens\": 800,\n      \"skill_tokens\": 800\n    },\n    \"selected_files\": [\n      {\n        \"file\": \"app.py\",\n        \"score\": 1.95,\n        \"tokens_est\": 27,\n        \"reasons\": [\n          \"impact\"\n        ]\n      }\n    ],\n    \"selected_file_count\": 1,\n    \"skills_count\": 0,\n    \"memories_count\": 0,\n    \"tokens_est\": 62,\n    \"context_file\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n    \"created_at\": \"2026-04-28T01:01:06.223006+00:00\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "openclaw-run",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo",
        "--task",
        "fix ok function",
        "--agent",
        "leader"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"OCLAW-762cbcb86f44\",\n  \"task\": \"fix ok function\",\n  \"agent\": \"leader\",\n  \"real\": false,\n  \"prompt\": {\n    \"status\": \"ok\",\n    \"agent\": \"leader\",\n    \"prompt_file\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/openclaw/latest_openclaw_prompt.md\",\n    \"prompt_chars\": 642,\n    \"context_mode\": \"budget\",\n    \"context_meta\": {\n      \"status\": \"ok\",\n      \"task\": \"fix ok function\",\n      \"profile\": \"medium\",\n      \"task_class\": {\n        \"size\": \"small\",\n        \"reason\": \"heuristic_score:1\",\n        \"word_count\": 3\n      },\n      \"budget\": {\n        \"max_tokens\": 8000,\n        \"max_files\": 8,\n        \"per_file_tokens\": 1000,\n        \"memory_tokens\": 800,\n        \"skill_tokens\": 800\n      },\n      \"selected_files\": [\n        {\n          \"file\": \"app.py\",\n          \"score\": 1.95,\n          \"tokens_est\": 27,\n          \"reasons\": [\n            \"impact\"\n          ]\n        }\n      ],\n      \"selected_file_count\": 1,\n      \"skills_count\": 0,\n      \"memories_count\": 0,\n      \"tokens_est\": 62,\n      \"context_file\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n      \"created_at\": \"2026-04-28T01:01:06.393782+00:00\"\n    }\n  },\n  \"created_at\": \"2026-04-28T01:01:06.394142+00:00\",\n  \"status\": \"dry_run\",\n  \"instruction\": \"Copy prompt_file content into OpenClaw manually or run with --real after enabling allowed_real_run.\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "openclaw-summary",
        "--repo",
        "/mnt/data/uacos_phase24_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"runs\": 1,\n  \"by_status\": {\n    \"dry_run\": 1\n  },\n  \"recent\": [\n    {\n      \"id\": \"OCLAW-762cbcb86f44\",\n      \"task\": \"fix ok function\",\n      \"agent\": \"leader\",\n      \"real\": false,\n      \"prompt\": {\n        \"status\": \"ok\",\n        \"agent\": \"leader\",\n        \"prompt_file\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/openclaw/latest_openclaw_prompt.md\",\n        \"prompt_chars\": 642,\n        \"context_mode\": \"budget\",\n        \"context_meta\": {\n          \"status\": \"ok\",\n          \"task\": \"fix ok function\",\n          \"profile\": \"medium\",\n          \"task_class\": {\n            \"size\": \"small\",\n            \"reason\": \"heuristic_score:1\",\n            \"word_count\": 3\n          },\n          \"budget\": {\n            \"max_tokens\": 8000,\n            \"max_files\": 8,\n            \"per_file_tokens\": 1000,\n            \"memory_tokens\": 800,\n            \"skill_tokens\": 800\n          },\n          \"selected_files\": [\n            {\n              \"file\": \"app.py\",\n              \"score\": 1.95,\n              \"tokens_est\": 27,\n              \"reasons\": [\n                \"impact\"\n              ]\n            }\n          ],\n          \"selected_file_count\": 1,\n          \"skills_count\": 0,\n          \"memories_count\": 0,\n          \"tokens_est\": 62,\n          \"context_file\": \"/mnt/data/uacos_phase24_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n          \"created_at\": \"2026-04-28T01:01:06.393782+00:00\"\n        }\n      },\n      \"created_at\": \"2026-04-28T01:01:06.394142+00:00\",\n      \"status\": \"dry_run\",\n      \"instruction\": \"Copy prompt_file content into OpenClaw manually or run with --real after enabling allowed_real_run.\",\n      \"ts\": \"2026-04-28T01:01:06.394149+00:00\"\n    }\n  ]\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_25_TEST_REPORT.md`

# Phase 25 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_prod": true,
    "cli_all_ok": true,
    "metrics_json_exists": true,
    "dashboard_html_exists": true,
    "doctor_pass": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE25_SMOKE_OK\nhealth= green\nscore= 100\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve} ...\n\nUniversal AI Context OS v3.0 - Phase 25 Production Dashboard Metrics\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstr",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase25_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-28T01:09:00.387890+00:00\",\n    \"finished_at\": \"2026-04-28T01:09:00.390188+00:00\"\n  },\n  \"created_at\": \"2026-04-28T01:09:00.390232+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "graph-build",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"graph_dir\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/graph\",\n  \"stats\": {\n    \"file_count\": 1,\n    \"file_edge_count\": 0,\n    \"call_edge_count\": 0,\n    \"symbol_count\": 1,\n    \"parse_errors\": 0\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "semantic-index",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"index_file\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/semantic_index.json\",\n  \"doc_count\": 0,\n  \"vocab_count\": 0,\n  \"provider\": \"local_tfidf\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "context-budget",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo",
        "--task",
        "check ok app",
        "--profile",
        "small"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"check ok app\",\n  \"profile\": \"small\",\n  \"task_class\": {\n    \"size\": \"tiny\",\n    \"reason\": \"heuristic_score:0\",\n    \"word_count\": 3\n  },\n  \"budget\": {\n    \"max_tokens\": 4500,\n    \"max_files\": 5,\n    \"per_file_tokens\": 850,\n    \"memory_tokens\": 500,\n    \"skill_tokens\": 500\n  },\n  \"selected_files\": [\n    {\n      \"file\": \"app.py\",\n      \"score\": 1.95,\n      \"tokens_est\": 29,\n      \"reasons\": [\n        \"impact\",\n        \"filename\"\n      ]\n    }\n  ],\n  \"selected_file_count\": 1,\n  \"skills_count\": 0,\n  \"memories_count\": 0,\n  \"tokens_est\": 64,\n  \"context_file\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n  \"created_at\": \"2026-04-28T01:09:00.984521+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "prod-metrics",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"created_at\": \"2026-04-28T01:09:01.166049+00:00\",\n  \"repo\": \"/mnt/data/uacos_phase25_cli_repo\",\n  \"health\": {\n    \"score\": 100,\n    \"level\": \"green\",\n    \"errors\": [],\n    \"warnings\": []\n  },\n  \"counts\": {\n    \"graph_files\": 1,\n    \"graph_symbols\": 1,\n    \"graph_calls\": 0,\n    \"semantic_docs\": 0,\n    \"autopilot_runs\": 0,\n    \"patch_runs\": 0,\n    \"skill_executions\": 0,\n    \"learning_events\": 0,\n    \"feedback_events\": 0,\n    \"tracked_skill_feedback\": 0,\n    \"provider_runs\": 0,\n    \"openclaw_runs\": 0,\n    \"budget_selected_files\": 1\n  },\n  \"statuses\": {\n    \"autopilot\": {},\n    \"patch\": {},\n    \"skill_execution\": {},\n    \"openclaw\": {},\n    \"provider\": {}\n  },\n  \"cost\": {\n    \"provider_estimated_cost_usd\": 0.0\n  },\n  \"latest\": {\n    \"budget_report\": {\n      \"status\": \"ok\",\n      \"task\": \"check ok app\",\n      \"profile\": \"small\",\n      \"task_class\": {\n        \"size\": \"tiny\",\n        \"reason\": \"heuristic_score:0\",\n        \"word_count\": 3\n      },\n      \"budget\": {\n        \"max_tokens\": 4500,\n        \"max_files\": 5,\n        \"per_file_tokens\": 850,\n        \"memory_tokens\": 500,\n        \"skill_tokens\": 500\n      },\n      \"selected_files\": [\n        {\n          \"file\": \"app.py\",\n          \"score\": 1.95,\n          \"tokens_est\": 29,\n          \"reasons\": [\n            \"impact\",\n            \"filename\"\n          ]\n        }\n      ],\n      \"selected_file_count\": 1,\n      \"skills_count\": 0,\n      \"memories_count\": 0,\n      \"tokens_est\": 64,\n      \"context_file\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n      \"created_at\": \"2026-04-28T01:09:00.984521+00:00\"\n    },\n    \"recent_autopilot\": [],\n    \"recent_patch\": [],\n    \"recent_provider\": [],\n    \"recent_openclaw\": [],\n    \"recent_feedback\": []\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "prod-report",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"report\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/metrics/production_metrics.json\",\n  \"metrics\": {\n    \"status\": \"ok\",\n    \"created_at\": \"2026-04-28T01:09:01.339385+00:00\",\n    \"repo\": \"/mnt/data/uacos_phase25_cli_repo\",\n    \"health\": {\n      \"score\": 100,\n      \"level\": \"green\",\n      \"errors\": [],\n      \"warnings\": []\n    },\n    \"counts\": {\n      \"graph_files\": 1,\n      \"graph_symbols\": 1,\n      \"graph_calls\": 0,\n      \"semantic_docs\": 0,\n      \"autopilot_runs\": 0,\n      \"patch_runs\": 0,\n      \"skill_executions\": 0,\n      \"learning_events\": 0,\n      \"feedback_events\": 0,\n      \"tracked_skill_feedback\": 0,\n      \"provider_runs\": 0,\n      \"openclaw_runs\": 0,\n      \"budget_selected_files\": 1\n    },\n    \"statuses\": {\n      \"autopilot\": {},\n      \"patch\": {},\n      \"skill_execution\": {},\n      \"openclaw\": {},\n      \"provider\": {}\n    },\n    \"cost\": {\n      \"provider_estimated_cost_usd\": 0.0\n    },\n    \"latest\": {\n      \"budget_report\": {\n        \"status\": \"ok\",\n        \"task\": \"check ok app\",\n        \"profile\": \"small\",\n        \"task_class\": {\n          \"size\": \"tiny\",\n          \"reason\": \"heuristic_score:0\",\n          \"word_count\": 3\n        },\n        \"budget\": {\n          \"max_tokens\": 4500,\n          \"max_files\": 5,\n          \"per_file_tokens\": 850,\n          \"memory_tokens\": 500,\n          \"skill_tokens\": 500\n        },\n        \"selected_files\": [\n          {\n            \"file\": \"app.py\",\n            \"score\": 1.95,\n            \"tokens_est\": 29,\n            \"reasons\": [\n              \"impact\",\n              \"filename\"\n            ]\n          }\n        ],\n        \"selected_file_count\": 1,\n        \"skills_count\": 0,\n        \"memories_count\": 0,\n        \"tokens_est\": 64,\n        \"context_file\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/budget/latest_budgeted_context.md\",\n        \"created_at\": \"2026-04-28T01:09:00.984521+00:00\"\n      },\n      \"recent_autopilot\": [],\n      \"recent_patch\": [],\n      \"recent_provider\": [],\n      \"recent_openclaw\": [],\n      \"recent_feedback\": []\n    }\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "prod-dashboard",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"dashboard\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/metrics/production_dashboard.html\",\n  \"health\": {\n    \"score\": 100,\n    \"level\": \"green\",\n    \"errors\": [],\n    \"warnings\": []\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "prod-doctor",
        "--repo",
        "/mnt/data/uacos_phase25_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"pass\",\n  \"checks\": [\n    {\n      \"name\": \"uacos_dir\",\n      \"status\": \"pass\"\n    },\n    {\n      \"name\": \"health_score\",\n      \"status\": \"pass\",\n      \"score\": 100\n    },\n    {\n      \"name\": \"metrics_report\",\n      \"status\": \"pass\",\n      \"path\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/metrics/production_metrics.json\"\n    },\n    {\n      \"name\": \"html_dashboard\",\n      \"status\": \"pass\",\n      \"path\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/metrics/production_dashboard.html\"\n    }\n  ],\n  \"health\": {\n    \"score\": 100,\n    \"level\": \"green\",\n    \"errors\": [],\n    \"warnings\": []\n  },\n  \"report\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/metrics/production_metrics.json\",\n  \"dashboard\": \"/mnt/data/uacos_phase25_cli_repo/.uacos/metrics/production_dashboard.html\"\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_26_TEST_REPORT.md`

# Phase 26 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_context_compressed": true,
    "cli_all_ok": true,
    "cache_exists": true,
    "summary_exists": true,
    "context_exists": true,
    "report_exists": true,
    "budget_respected": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE26_SMOKE_OK\nfiles= 3\ncache_ratio= 0.7952\ncontext_tokens= 673\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report} ...\n\nUniversal AI Context OS v3.1 - Phase 26 Context Compression Engine\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rul",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase26_cli_repo_fixed"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase26_cli_repo_fixed\",\n  \"db\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 3,\n    \"files_indexed\": 3,\n    \"files_skipped\": 0,\n    \"files_changed\": 3,\n    \"symbols_indexed\": 13,\n    \"started_at\": \"2026-04-28T01:24:22.087506+00:00\",\n    \"finished_at\": \"2026-04-28T01:24:22.090717+00:00\"\n  },\n  \"created_at\": \"2026-04-28T01:24:22.090778+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "memory-add",
        "--repo",
        "/mnt/data/uacos_phase26_cli_repo_fixed",
        "--kind",
        "project_truth",
        "--key",
        "user_flow",
        "--value",
        "UserService.create_user calls save_user"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"MEM-329c5ba5e2ce\",\n  \"kind\": \"project_truth\",\n  \"key\": \"user_flow\",\n  \"value\": \"UserService.create_user calls save_user\",\n  \"source\": \"user\",\n  \"confidence\": 1.0,\n  \"tags\": [],\n  \"applies_to\": [],\n  \"valid_at\": \"2026-04-28T01:24:22.274109+00:00\",\n  \"invalid_at\": null,\n  \"invalid_reason\": null,\n  \"created_at\": \"2026-04-28T01:24:22.274160+00:00\",\n  \"updated_at\": \"2026-04-28T01:24:22.274163+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "compress-cache",
        "--repo",
        "/mnt/data/uacos_phase26_cli_repo_fixed"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"updated\": 3,\n  \"skipped\": 0,\n  \"file_count\": 3,\n  \"raw_tokens_est\": 132,\n  \"summary_tokens_est\": 139,\n  \"compression_ratio\": 1.053,\n  \"cache_file\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/compression/summary_cache.json\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "project-summary",
        "--repo",
        "/mnt/data/uacos_phase26_cli_repo_fixed"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"summary_file\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/compression/project_compressed_summary.md\",\n  \"tokens_est\": 254,\n  \"cache\": {\n    \"status\": \"ok\",\n    \"updated\": 0,\n    \"skipped\": 3,\n    \"file_count\": 3,\n    \"raw_tokens_est\": 132,\n    \"summary_tokens_est\": 139,\n    \"compression_ratio\": 1.053,\n    \"cache_file\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/compression/summary_cache.json\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "context-compressed",
        "--repo",
        "/mnt/data/uacos_phase26_cli_repo_fixed",
        "--task",
        "fix save_user create_user bug",
        "--max-tokens",
        "4000"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"task\": \"fix save_user create_user bug\",\n  \"max_tokens\": 4000,\n  \"selected_files\": [\n    {\n      \"file\": \"db.py\",\n      \"score\": 1.5,\n      \"summary_tokens\": 72,\n      \"raw_tokens\": 96\n    },\n    {\n      \"file\": \"service.py\",\n      \"score\": 1.5,\n      \"summary_tokens\": 41,\n      \"raw_tokens\": 27\n    }\n  ],\n  \"selected_file_count\": 2,\n  \"raw_selected_tokens_est\": 123,\n  \"compressed_tokens_est\": 329,\n  \"compression_ratio_vs_selected_raw\": 2.6748,\n  \"context_file\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/compression/latest_compressed_context.md\",\n  \"created_at\": \"2026-04-28T01:24:22.712768+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "compression-report",
        "--repo",
        "/mnt/data/uacos_phase26_cli_repo_fixed"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"cache_file_count\": 3,\n  \"cache_raw_tokens_est\": 132,\n  \"cache_summary_tokens_est\": 139,\n  \"cache_compression_ratio\": 1.053,\n  \"latest_context\": {\n    \"status\": \"ok\",\n    \"task\": \"fix save_user create_user bug\",\n    \"max_tokens\": 4000,\n    \"selected_files\": [\n      {\n        \"file\": \"db.py\",\n        \"score\": 1.5,\n        \"summary_tokens\": 72,\n        \"raw_tokens\": 96\n      },\n      {\n        \"file\": \"service.py\",\n        \"score\": 1.5,\n        \"summary_tokens\": 41,\n        \"raw_tokens\": 27\n      }\n    ],\n    \"selected_file_count\": 2,\n    \"raw_selected_tokens_est\": 123,\n    \"compressed_tokens_est\": 329,\n    \"compression_ratio_vs_selected_raw\": 2.6748,\n    \"context_file\": \"/mnt/data/uacos_phase26_cli_repo_fixed/.uacos/compression/latest_compressed_context.md\",\n    \"created_at\": \"2026-04-28T01:24:22.712768+00:00\"\n  }\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_27_TEST_REPORT.md`

# Phase 27 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_tx": true,
    "cli_all_ok": true,
    "tx_dir_exists": true,
    "cli_committed": true,
    "patch_applied": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE27_SMOKE_OK\ntransactions= 2\nbad_status= rolled_back\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report,tx-begin,tx-run,tx-rollback,tx-status,tx-list,tx-report} ...\n\nUniversal AI Context OS v3.2 - Phase 27 Transactional Autopilot\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memor",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase27_cli_repo_fixed"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase27_cli_repo_fixed\",\n  \"db\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 2,\n    \"files_indexed\": 1,\n    \"files_skipped\": 1,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-28T01:43:24.509581+00:00\",\n    \"finished_at\": \"2026-04-28T01:43:24.512654+00:00\"\n  },\n  \"created_at\": \"2026-04-28T01:43:24.512714+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "tx-run",
        "--repo",
        "/mnt/data/uacos_phase27_cli_repo_fixed",
        "--patch",
        "/mnt/data/uacos_phase27_cli_repo_fixed/change.diff",
        "--allowed-file",
        "app.py",
        "--test",
        "python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"TX-e7f5d7f9363c\",\n  \"status\": \"committed\",\n  \"title\": \"Transactional patch\",\n  \"objective\": \"\",\n  \"repo\": \"/mnt/data/uacos_phase27_cli_repo_fixed\",\n  \"files\": [\n    \"app.py\"\n  ],\n  \"tests\": [\n    \"python -S -c \\\"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\\\"\"\n  ],\n  \"checkpoint\": {\n    \"status\": \"ok\",\n    \"saved\": [\n      {\n        \"path\": \"app.py\",\n        \"checkpoint\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/transactions/TX-e7f5d7f9363c/checkpoint/app.py\"\n      }\n    ],\n    \"missing\": [],\n    \"checkpoint_dir\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/transactions/TX-e7f5d7f9363c/checkpoint\"\n  },\n  \"patch_manifest\": {\n    \"id\": \"PATCH-51c1558b798f\",\n    \"status\": \"applied\",\n    \"patch_file\": \"/mnt/data/uacos_phase27_cli_repo_fixed/change.diff\",\n    \"validation\": {\n      \"status\": \"pass\",\n      \"file_count\": 1,\n      \"files\": [\n        {\n          \"old_path\": \"app.py\",\n          \"new_path\": \"app.py\",\n          \"operation\": \"modify\",\n          \"headers\": [\n            \"diff --git a/app.py b/app.py\",\n            \"--- a/app.py\",\n            \"+++ b/app.py\"\n          ],\n          \"hunks\": [\n            {\n              \"header\": \"@@ -1,2 +1,2 @@\",\n              \"lines\": [\n                \" def value():\",\n                \"-    return 1\",\n                \"+    return 42\"\n              ]\n            }\n          ],\n          \"path\": \"app.py\"\n        }\n      ],\n      \"findings\": []\n    },\n    \"dry_run\": false,\n    \"changed\": [\n      {\n        \"operation\": \"modify\",\n        \"path\": \"app.py\",\n        \"backup\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/patch_runs/PATCH-51c1558b798f/backup/app.py\",\n        \"notes\": []\n      }\n    ],\n    \"tests\": [],\n    \"created_at\": \"2026-04-28T01:43:24.892576+00:00\",\n    \"run_dir\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/patch_runs/PATCH-51c1558b798f\",\n    \"manifest_file\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/patch_runs/PATCH-51c1558b798f/manifest.json\"\n  },\n  \"test_results\": [\n    {\n      \"command\": \"python -S -c \\\"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\\\"\",\n      \"returncode\": 0,\n      \"stdout\": \"\",\n      \"stderr\": \"\",\n      \"ok\": true\n    }\n  ],\n  \"events\": [\n    {\n      \"ts\": \"2026-04-28T01:43:24.891346+00:00\",\n      \"event\": \"transaction_created\",\n      \"data\": {\n        \"files\": [\n          \"app.py\"\n        ],\n        \"tests\": [\n          \"python -S -c \\\"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\\\"\"\n        ]\n      }\n    },\n    {\n      \"ts\": \"2026-04-28T01:43:24.891849+00:00\",\n      \"event\": \"patch_validated\",\n      \"data\": {\n        \"status\": \"pass\",\n        \"file_count\": 1\n      }\n    },\n    {\n      \"ts\": \"2026-04-28T01:43:24.893658+00:00\",\n      \"event\": \"patch_applied\",\n      \"data\": {\n        \"status\": \"applied\"\n      }\n    },\n    {\n      \"ts\": \"2026-04-28T01:43:24.982286+00:00\",\n      \"event\": \"tests_completed\",\n      \"data\": {\n        \"failed\": false,\n        \"count\": 1\n      }\n    },\n    {\n      \"ts\": \"2026-04-28T01:43:24.982815+00:00\",\n      \"event\": \"transaction_committed\",\n      \"data\": {}\n    }\n  ],\n  \"created_at\": \"2026-04-28T01:43:24.890911+00:00\",\n  \"updated_at\": \"2026-04-28T01:43:24.983185+00:00\",\n  \"manifest_file\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/transactions/TX-e7f5d7f9363c/manifest.json\",\n  \"dry_run\": false,\n  \"patch_file\": \"/mnt/data/uacos_phase27_cli_repo_fixed/change.diff\",\n  \"validation\": {\n    \"status\": \"pass\",\n    \"file_count\": 1,",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "tx-list",
        "--repo",
        "/mnt/data/uacos_phase27_cli_repo_fixed"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"count\": 1,\n  \"transactions\": [\n    {\n      \"id\": \"TX-e7f5d7f9363c\",\n      \"status\": \"committed\",\n      \"title\": \"Transactional patch\",\n      \"updated_at\": \"2026-04-28T01:43:24.983185+00:00\",\n      \"manifest_file\": \"/mnt/data/uacos_phase27_cli_repo_fixed/.uacos/transactions/TX-e7f5d7f9363c/manifest.json\"\n    }\n  ]\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_28_TEST_REPORT.md`

# Phase 28 Test Report

```json
{
  "checks": {
    "smoke_ok": true,
    "help_has_runtime": true,
    "cli_all_ok": true,
    "runtime_dir_exists": true,
    "job_file_exists": true,
    "prompt_created": true,
    "waiting_manual": true
  },
  "smoke": {
    "returncode": 0,
    "stdout": "PHASE28_SMOKE_OK\njob= JOB-11e622e30039\nstatus= waiting_manual\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report,tx-begin,tx-run,tx-rollback,tx-status,tx-list,tx-report,runtime-init,runtime-config,runtime-validate,runtime-status,job-create,job-run-once,job-list,job-status,job-report} ...\n\nUniversal AI Context OS v3.3 - Phase 28 True Agent Runtime\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,t",
    "stderr": ""
  },
  "cli_results": [
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "bootstrap",
        "--repo",
        "/mnt/data/uacos_phase28_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"repo\": \"/mnt/data/uacos_phase28_cli_repo\",\n  \"db\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/repo_index.sqlite\",\n  \"agent_registry\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/agents.json\",\n  \"adapter_config\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/adapters.json\",\n  \"scan_result\": {\n    \"scan_run_id\": 1,\n    \"files_seen\": 1,\n    \"files_indexed\": 1,\n    \"files_skipped\": 0,\n    \"files_changed\": 1,\n    \"symbols_indexed\": 1,\n    \"started_at\": \"2026-04-28T01:53:01.813114+00:00\",\n    \"finished_at\": \"2026-04-28T01:53:01.815989+00:00\"\n  },\n  \"created_at\": \"2026-04-28T01:53:01.816029+00:00\"\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "runtime-init",
        "--repo",
        "/mnt/data/uacos_phase28_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"config\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/runtime/runtime_config.json\",\n  \"config_data\": {\n    \"version\": 1,\n    \"mode\": \"dry_run\",\n    \"default_backend\": \"manual\",\n    \"provider\": \"dry_run\",\n    \"openclaw_agent\": \"leader\",\n    \"max_context_tokens\": 6000,\n    \"max_context_files\": 8,\n    \"require_transaction\": true,\n    \"auto_apply_patch\": false,\n    \"allowed_real_run\": false,\n    \"job_lock_timeout_sec\": 600\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "runtime-validate",
        "--repo",
        "/mnt/data/uacos_phase28_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"pass\",\n  \"findings\": [],\n  \"config\": {\n    \"version\": 1,\n    \"mode\": \"dry_run\",\n    \"default_backend\": \"manual\",\n    \"provider\": \"dry_run\",\n    \"openclaw_agent\": \"leader\",\n    \"max_context_tokens\": 6000,\n    \"max_context_files\": 8,\n    \"require_transaction\": true,\n    \"auto_apply_patch\": false,\n    \"allowed_real_run\": false,\n    \"job_lock_timeout_sec\": 600\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "job-create",
        "--repo",
        "/mnt/data/uacos_phase28_cli_repo",
        "--task",
        "fix value function",
        "--backend",
        "manual",
        "--allowed-file",
        "app.py"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"JOB-2f931e1705db\",\n  \"status\": \"queued\",\n  \"task\": \"fix value function\",\n  \"backend\": \"manual\",\n  \"allowed_files\": [\n    \"app.py\"\n  ],\n  \"allowed_dirs\": [],\n  \"tests\": [],\n  \"auto_apply\": false,\n  \"created_at\": \"2026-04-28T01:53:02.373865+00:00\",\n  \"updated_at\": \"2026-04-28T01:53:02.373900+00:00\",\n  \"events\": [\n    {\n      \"ts\": \"2026-04-28T01:53:02.373903+00:00\",\n      \"event\": \"queued\"\n    }\n  ]\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "job-run-once",
        "--repo",
        "/mnt/data/uacos_phase28_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"id\": \"JOB-2f931e1705db\",\n  \"status\": \"waiting_manual\",\n  \"task\": \"fix value function\",\n  \"backend\": \"manual\",\n  \"allowed_files\": [\n    \"app.py\"\n  ],\n  \"allowed_dirs\": [],\n  \"tests\": [],\n  \"auto_apply\": false,\n  \"created_at\": \"2026-04-28T01:53:02.373865+00:00\",\n  \"updated_at\": \"2026-04-28T01:53:02.558526+00:00\",\n  \"events\": [\n    {\n      \"ts\": \"2026-04-28T01:53:02.373903+00:00\",\n      \"event\": \"queued\"\n    },\n    {\n      \"ts\": \"2026-04-28T01:53:02.546453+00:00\",\n      \"event\": \"started\",\n      \"data\": {\n        \"real\": false\n      }\n    },\n    {\n      \"ts\": \"2026-04-28T01:53:02.558512+00:00\",\n      \"event\": \"context_prepared\",\n      \"data\": {\n        \"tokens\": 83,\n        \"files\": 1\n      }\n    },\n    {\n      \"ts\": \"2026-04-28T01:53:02.558519+00:00\",\n      \"event\": \"manual_prompt_ready\",\n      \"data\": {\n        \"status\": \"manual_waiting\",\n        \"prompt_file\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/runtime/JOB-2f931e1705db_prompt.md\"\n      }\n    }\n  ],\n  \"prompt_file\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/runtime/JOB-2f931e1705db_prompt.md\",\n  \"context_file\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/compression/latest_compressed_context.md\",\n  \"backend_result\": {\n    \"status\": \"manual_waiting\",\n    \"prompt_file\": \"/mnt/data/uacos_phase28_cli_repo/.uacos/runtime/JOB-2f931e1705db_prompt.md\"\n  }\n}\n",
      "stderr": ""
    },
    {
      "cmd": [
        "/opt/pyvenv/bin/python",
        "-S",
        "-m",
        "uacos.cli",
        "runtime-status",
        "--repo",
        "/mnt/data/uacos_phase28_cli_repo"
      ],
      "returncode": 0,
      "stdout": "{\n  \"status\": \"ok\",\n  \"validation\": {\n    \"status\": \"pass\",\n    \"findings\": [],\n    \"config\": {\n      \"version\": 1,\n      \"mode\": \"dry_run\",\n      \"default_backend\": \"manual\",\n      \"provider\": \"dry_run\",\n      \"openclaw_agent\": \"leader\",\n      \"max_context_tokens\": 6000,\n      \"max_context_files\": 8,\n      \"require_transaction\": true,\n      \"auto_apply_patch\": false,\n      \"allowed_real_run\": false,\n      \"job_lock_timeout_sec\": 600\n    }\n  },\n  \"jobs\": 1,\n  \"by_status\": {\n    \"waiting_manual\": 1\n  },\n  \"recent_history\": [\n    {\n      \"event\": \"job_created\",\n      \"job_id\": \"JOB-2f931e1705db\",\n      \"status\": \"queued\",\n      \"backend\": \"manual\",\n      \"ts\": \"2026-04-28T01:53:02.374201+00:00\"\n    },\n    {\n      \"event\": \"job_finished\",\n      \"job_id\": \"JOB-2f931e1705db\",\n      \"status\": \"waiting_manual\",\n      \"backend\": \"manual\",\n      \"ts\": \"2026-04-28T01:53:02.558781+00:00\"\n    }\n  ]\n}\n",
      "stderr": ""
    }
  ]
}
```

---

## Source: `PHASE_29_TEST_REPORT.md`

# Phase 29 Test Report

```json
{
  "checks": {
    "phase29_tests_ok": true,
    "cli_help_ok": true,
    "compile_ok": true,
    "test_report_exists": true
  },
  "test": {
    "returncode": 0,
    "stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                               [100%]\u001b[0m\n\nSpreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n\nPHASE29_TEST_MODE= pytest-targeted\nPHASE29_TEST_REPORT= /mnt/data/uacos_phase29_test_hardening/test_results_phase29.json\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report,tx-begin,tx-run,tx-rollback,tx-status,tx-list,tx-report,runtime-init,runtime-config,runtime-validate,runtime-status,job-create,job-run-once,job-list,job-status,job-report} ...\n\nUniversal AI Context OS v3.3 - Phase 28 True Agent Runtime\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,t",
    "stderr": ""
  },
  "compile": {
    "returncode": 0,
    "stdout": "",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  }
}
```

---

## Source: `PHASE_30_TEST_REPORT.md`

# Phase 30 Test Report

```json
{
  "checks": {
    "phase30_tests_ok": true,
    "phase30_script_ok": true,
    "cli_help_ok": true,
    "compile_ok": true
  },
  "test": {
    "returncode": 0,
    "stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                                      [100%]\u001b[0m\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "script": {
    "returncode": 0,
    "stdout": "output_per_1k\": 0.0\n            }\n          },\n          \"result\": {\n            \"status\": \"ok\",\n            \"provider\": \"mock_openai\",\n            \"model\": \"mock-model\",\n            \"content\": \"diff --git a/app.py b/app.py\\n--- a/app.py\\n+++ b/app.py\\n@@ -1,2 +1,2 @@\\n def value():\\n-    return 1\\n+    return 42\\n\",\n            \"raw\": {\n              \"id\": \"mock-uacos\",\n              \"object\": \"chat.completion\",\n              \"choices\": [\n                {\n                  \"index\": 0,\n                  \"message\": {\n                    \"role\": \"assistant\",\n                    \"content\": \"diff --git a/app.py b/app.py\\n--- a/app.py\\n+++ b/app.py\\n@@ -1,2 +1,2 @@\\n def value():\\n-    return 1\\n+    return 42\\n\"\n                  },\n                  \"finish_reason\": \"stop\"\n                }\n              ],\n              \"usage\": {\n                \"prompt_tokens\": 100,\n                \"completion_tokens\": 50,\n                \"total_tokens\": 150\n              }\n            },\n            \"created_at\": \"2026-04-28T03:06:07.710071+00:00\"\n          }\n        },\n        \"diff_file\": \"/tmp/tmphqri7f5m/repo/.uacos/runtime/JOB-2f74d3151491.diff\",\n        \"transaction\": {\n          \"id\": \"TX-058280198b3e\",\n          \"status\": \"committed\",\n          \"title\": \"Runtime job JOB-2f74d3151491\",\n          \"objective\": \"Change app.value from 1 to 42\",\n          \"repo\": \"/tmp/tmphqri7f5m/repo\",\n          \"files\": [\n            \"app.py\"\n          ],\n          \"tests\": [\n            \"python -S -c \\\"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\\\"\"\n          ],\n          \"checkpoint\": {\n            \"status\": \"ok\",\n            \"saved\": [\n              {\n                \"path\": \"app.py\",\n                \"checkpoint\": \"/tmp/tmphqri7f5m/repo/.uacos/transactions/TX-058280198b3e/checkpoint/app.py\"\n              }\n            ],\n            \"missing\": [],\n            \"checkpoint_dir\": \"/tmp/tmphqri7f5m/repo/.uacos/transactions/TX-058280198b3e/checkpoint\"\n          },\n          \"patch_manifest\": {\n            \"id\": \"PATCH-65df33549878\",\n            \"status\": \"applied\",\n            \"patch_file\": \"/tmp/tmphqri7f5m/repo/.uacos/runtime/JOB-2f74d3151491.diff\",\n            \"validation\": {\n              \"status\": \"pass\",\n              \"file_count\": 1,\n              \"files\": [\n                {\n                  \"old_path\": \"app.py\",\n                  \"new_path\": \"app.py\",\n                  \"operation\": \"modify\",\n                  \"headers\": [\n                    \"diff --git a/app.py b/app.py\",\n                    \"--- a/app.py\",\n                    \"+++ b/app.py\"\n                  ],\n                  \"hunks\": [\n                    {\n                      \"header\": \"@@ -1,2 +1,2 @@\",\n                      \"lines\": [\n                        \" def value():\",\n                        \"-    return 1\",\n                        \"+    return 42\"\n                      ]\n                    }\n                  ],\n                  \"path\": \"app.py\"\n                }\n              ],\n              \"findings\": []\n            },\n            \"dry_run\": false,\n            \"changed\": [\n              {\n                \"operation\": \"modify\",\n                \"path\": \"app.py\",\n                \"backup\": \"/tmp/tmphqri7f5m/repo/.uacos/patch_runs/PATCH-65df33549878/backup/app.py\",\n                \"notes\": []\n              }\n            ],\n            \"tests\": [],\n            \"created_at\": \"2026-04-28T03:06:07.713397+00:00\",\n            \"run_dir\": \"/tmp/tmphqri7f5m/repo/.uacos/patch_runs/PATCH-65df33549878\",\n            \"manifest_file\": \"/tmp/tmphqri7f5m/repo/.uacos/patch_runs/PATCH-65df33549878/manifest.json\"\n          },\n          \"test_results\": [\n            {\n              \"command\": \"python -S -c \\\"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\\\"\",\n              \"returncode\": 0,\n              \"stdout\": \"\",\n              \"stderr\": \"\",\n              \"ok\": true\n            }\n          ],\n          \"events\": [\n            {\n              \"ts\": \"2026-04-28T03:06:07.712718+00:00\",\n              \"event\": \"transaction_created\",\n              \"data\": {\n                \"files\": [\n                  \"app.py\"\n                ],\n                \"tests\": [\n                  \"python -S -c \\\"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\\\"\"\n                ]\n              }\n            },\n            {\n              \"ts\": \"2026-04-28T03:06:07.712975+00:00\",\n              \"event\": \"patch_validated\",\n              \"data\": {\n                \"status\": \"pass\",\n                \"file_count\": 1\n              }\n            },\n            {\n              \"ts\": \"2026-04-28T03:06:07.714902+00:00\",\n              \"event\": \"patch_applied\",\n              \"data\": {\n                \"status\": \"applied\"\n              }\n            },\n            {\n              \"ts\": \"2026-04-28T03:06:07.778670+00:00\",\n              \"event\": \"tests_completed\",\n              \"data\": {\n                \"failed\": false,\n                \"count\": 1\n              }\n            },\n            {\n              \"ts\": \"2026-04-28T03:06:07.779349+00:00\",\n              \"event\": \"transaction_committed\",\n              \"data\": {}\n            }\n          ],\n          \"created_at\": \"2026-04-28T03:06:07.712494+00:00\",\n          \"updated_at\": \"2026-04-28T03:06:07.779899+00:00\",\n          \"manifest_file\": \"/tmp/tmphqri7f5m/repo/.uacos/transactions/TX-058280198b3e/manifest.json\",\n          \"dry_run\": false,\n          \"patch_file\": \"/tmp/tmphqri7f5m/repo/.uacos/runtime/JOB-2f74d3151491.diff\",\n          \"validation\": {\n            \"status\": \"pass\",\n            \"file_count\": 1,\n            \"files\": [\n              {\n                \"old_path\": \"app.py\",\n                \"new_path\": \"app.py\",\n                \"operation\": \"modify\",\n                \"headers\": [\n                  \"diff --git a/app.py b/app.py\",\n                  \"--- a/app.py\",\n                  \"+++ b/app.py\"\n                ],\n                \"hunks\": [\n                  {\n                    \"header\": \"@@ -1,2 +1,2 @@\",\n                    \"lines\": [\n                      \" def value():\",\n                      \"-    return 1\",\n                      \"+    return 42\"\n                    ]\n                  }\n                ],\n                \"path\": \"app.py\"\n              }\n            ],\n            \"findings\": []\n          },\n          \"metrics_after\": {\n            \"score\": 95,\n            \"level\": \"green\",\n            \"errors\": [],\n            \"warnings\": []\n          }\n        }\n      },\n      \"report_file\": \"/tmp/tmphqri7f5m/repo/.uacos/validation/phase30_realrun_report.json\"\n    }\n  ],\n  \"report_file\": \"/tmp/tmphqri7f5m/repo/.uacos/validation/phase30_realrun_report.json\"\n}\n\nSpreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n\nPHASE30_VALIDATION_REPORT= /mnt/data/uacos_phase30_realrun_validation/phase30_validation_result.json\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report,tx-begin,tx-run,tx-rollback,tx-status,tx-list,tx-report,runtime-init,runtime-config,runtime-validate,runtime-status,job-create,job-run-once,job-list,job-status,job-report,realrun-preflight,mock-provider-e2e,runtime-mock-e2e,ollama-realrun-check,openclaw-realrun-check,phase30-validate} ...\n\nUniversal AI Context OS v3.5 - Phase 30 Real-run E2E Validation\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute",
    "stderr": ""
  },
  "compile": {
    "returncode": 0,
    "stdout": "",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  }
}
```

---

## Source: `PHASE_31_TEST_REPORT.md`

# Phase 31 Test Report

```json
{
  "checks": {
    "phase31_tests_ok": true,
    "phase31_script_ok": true,
    "cli_help_ok": true,
    "compile_ok": true
  },
  "test": {
    "returncode": 0,
    "stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                                       [100%]\u001b[0m\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "script": {
    "returncode": 0,
    "stdout": "{\n  \"status\": \"pass\",\n  \"port\": 37075,\n  \"tools_count\": 7,\n  \"context_status\": \"ok\",\n  \"validate_status\": \"validated\",\n  \"apply_status\": \"applied\",\n  \"runtime_status\": {\n    \"status\": \"ok\",\n    \"validation\": {\n      \"status\": \"pass\",\n      \"findings\": [],\n      \"config\": {\n        \"version\": 1,\n        \"mode\": \"dry_run\",\n        \"default_backend\": \"manual\",\n        \"provider\": \"dry_run\",\n        \"openclaw_agent\": \"leader\",\n        \"max_context_tokens\": 6000,\n        \"max_context_files\": 8,\n        \"require_transaction\": true,\n        \"auto_apply_patch\": false,\n        \"allowed_real_run\": false,\n        \"job_lock_timeout_sec\": 600\n      }\n    },\n    \"jobs\": 0,\n    \"by_status\": {},\n    \"recent_history\": []\n  }\n}\n\nSpreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n\nPHASE31_VALIDATION_REPORT= /mnt/data/uacos_phase31_mcp_server/phase31_validation_result.json\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report,tx-begin,tx-run,tx-rollback,tx-status,tx-list,tx-report,runtime-init,runtime-config,runtime-validate,runtime-status,job-create,job-run-once,job-list,job-status,job-report,realrun-preflight,mock-provider-e2e,runtime-mock-e2e,ollama-realrun-check,openclaw-realrun-check,phase30-validate,mcp-serve,mcp-self-test,mcp-call} ...\n\nUniversal AI Context OS v3.6 - Phase 31 Minimal MCP Server\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan",
    "stderr": ""
  },
  "compile": {
    "returncode": 0,
    "stdout": "",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  }
}
```

---

## Source: `PHASE_32_TEST_REPORT.md`

# Phase 32 Test Report

```json
{
  "checks": {
    "phase32_tests_ok": true,
    "phase32_script_ok": true,
    "cli_help_ok": true,
    "compile_ok": true
  },
  "test": {
    "returncode": 0,
    "stdout": "\u001b[32m.\u001b[0m\u001b[32m.\u001b[0m\u001b[32m                                                                       [100%]\u001b[0m\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "script": {
    "returncode": 0,
    "stdout": "artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 704, in _warm_collaboration_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\\\", line 35986, in hydrate_crdt_from_proto\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\\\", line 747, in __call__\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\\\", line 150, in call\\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\\n\"\n    },\n    {\n      \"cmd\": [\n        \"/opt/pyvenv/bin/python\",\n        \"-m\",\n        \"uacos.cli\",\n        \"fullstack-index\",\n        \"--repo\",\n        \"/tmp/tmppuxdx00y/repo\"\n      ],\n      \"returncode\": 0,\n      \"stdout\": \"{\\n  \\\"status\\\": \\\"ok\\\",\\n  \\\"created_at\\\": \\\"2026-04-28T03:57:47.611841+00:00\\\",\\n  \\\"python\\\": {\\n    \\\"graph_stats\\\": {\\n      \\\"file_count\\\": 1,\\n      \\\"file_edge_count\\\": 0,\\n      \\\"call_edge_count\\\": 2,\\n      \\\"symbol_count\\\": 1,\\n      \\\"parse_errors\\\": 0\\n    },\\n    \\\"routes\\\": [\\n      {\\n        \\\"method\\\": \\\"GET\\\",\\n        \\\"endpoint\\\": \\\"/api/users\\\",\\n        \\\"file\\\": \\\"backend/api.py\\\",\\n        \\\"lineno\\\": 3\\n      }\\n    ]\\n  },\\n  \\\"javascript\\\": {\\n    \\\"file_count\\\": 1,\\n    \\\"files\\\": [\\n      {\\n        \\\"path\\\": \\\"frontend/dashboard.js\\\",\\n        \\\"language\\\": \\\"javascript\\\",\\n        \\\"sha256\\\": \\\"1829bda031fdd6769c9b247899410d847bb55c4d6a0d1907079ce44c17b2a41b\\\",\\n        \\\"line_count\\\": 2,\\n        \\\"imports\\\": [],\\n        \\\"functions\\\": [\\n          {\\n            \\\"name\\\": \\\"loadUsers\\\",\\n            \\\"lineno\\\": 1,\\n            \\\"kind\\\": \\\"function\\\"\\n          }\\n        ],\\n        \\\"classes\\\": [],\\n        \\\"calls\\\": [\\n          {\\n            \\\"callee\\\": \\\"loadUsers\\\",\\n            \\\"lineno\\\": 1\\n          },\\n          {\\n            \\\"callee\\\": \\\"fetch\\\",\\n            \\\"lineno\\\": 1\\n          }\\n        ],\\n        \\\"api_calls\\\": [\\n          {\\n            \\\"endpoint\\\": \\\"/api/users\\\",\\n            \\\"lineno\\\": 1,\\n            \\\"kind\\\": \\\"fetch_or_axios\\\"\\n          }\\n        ],\\n        \\\"routes\\\": [],\\n        \\\"parse_error\\\": null\\n      }\\n    ],\\n    \\\"api_calls\\\": [\\n      {\\n        \\\"file\\\": \\\"frontend/dashboard.js\\\",\\n        \\\"endpoint\\\": \\\"/api/users\\\",\\n        \\\"lineno\\\": 1,\\n        \\\"kind\\\": \\\"fetch_or_axios\\\"\\n      }\\n    ]\\n  },\\n  \\\"links\\\": [\\n    {\\n      \\\"backend_file\\\": \\\"backend/api.py\\\",\\n      \\\"frontend_file\\\": \\\"frontend/dashboard.js\\\",\\n      \\\"endpoint\\\": \\\"/api/users\\\",\\n      \\\"method\\\": \\\"GET\\\",\\n      \\\"route_lineno\\\": 3,\\n      \\\"call_lineno\\\": 1\\n    }\\n  ],\\n  \\\"stats\\\": {\\n    \\\"python_routes\\\": 1,\\n    \\\"js_files\\\": 1,\\n    \\\"frontend_api_calls\\\": 1,\\n    \\\"backend_frontend_links\\\": 1\\n  }\\n}\\n\",\n      \"stderr\": \"rm_spreadsheet_runtime_on_startup.py\\\", line 26, in warm_spreadsheet_runtime_on_startup\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 785, in warm_spreadsheet_runtime\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 720, in _warm_feature_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 704, in _warm_collaboration_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\\\", line 35986, in hydrate_crdt_from_proto\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\\\", line 747, in __call__\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\\\", line 150, in call\\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\\n\"\n    },\n    {\n      \"cmd\": [\n        \"/opt/pyvenv/bin/python\",\n        \"-m\",\n        \"uacos.cli\",\n        \"fullstack-impact\",\n        \"--repo\",\n        \"/tmp/tmppuxdx00y/repo\",\n        \"--task\",\n        \"fix /api/users dashboard\"\n      ],\n      \"returncode\": 0,\n      \"stdout\": \"{\\n  \\\"status\\\": \\\"ok\\\",\\n  \\\"task\\\": \\\"fix /api/users dashboard\\\",\\n  \\\"stats\\\": {\\n    \\\"python_routes\\\": 1,\\n    \\\"js_files\\\": 1,\\n    \\\"frontend_api_calls\\\": 1,\\n    \\\"backend_frontend_links\\\": 1\\n  },\\n  \\\"impacted_files\\\": [\\n    {\\n      \\\"file\\\": \\\"backend/api.py\\\",\\n      \\\"score\\\": 1.5,\\n      \\\"reasons\\\": [\\n        \\\"python_impact\\\",\\n        \\\"backend_route:/api/users\\\"\\n      ]\\n    },\\n    {\\n      \\\"file\\\": \\\"frontend/dashboard.js\\\",\\n      \\\"score\\\": 1.3,\\n      \\\"reasons\\\": [\\n        \\\"js_keyword_api\\\",\\n        \\\"frontend_calls:/api/users\\\"\\n      ]\\n    }\\n  ],\\n  \\\"links\\\": [\\n    {\\n      \\\"backend_file\\\": \\\"backend/api.py\\\",\\n      \\\"frontend_file\\\": \\\"frontend/dashboard.js\\\",\\n      \\\"endpoint\\\": \\\"/api/users\\\",\\n      \\\"method\\\": \\\"GET\\\",\\n      \\\"route_lineno\\\": 3,\\n      \\\"call_lineno\\\": 1\\n    }\\n  ]\\n}\\n\",\n      \"stderr\": \"rm_spreadsheet_runtime_on_startup.py\\\", line 26, in warm_spreadsheet_runtime_on_startup\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 785, in warm_spreadsheet_runtime\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 720, in _warm_feature_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 704, in _warm_collaboration_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\\\", line 35986, in hydrate_crdt_from_proto\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\\\", line 747, in __call__\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\\\", line 150, in call\\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\\n\"\n    },\n    {\n      \"cmd\": [\n        \"/opt/pyvenv/bin/python\",\n        \"-m\",\n        \"uacos.cli\",\n        \"fullstack-context\",\n        \"--repo\",\n        \"/tmp/tmppuxdx00y/repo\",\n        \"--task\",\n        \"fix /api/users dashboard\"\n      ],\n      \"returncode\": 0,\n      \"stdout\": \"{\\n  \\\"status\\\": \\\"ok\\\",\\n  \\\"task\\\": \\\"fix /api/users dashboard\\\",\\n  \\\"selected_files\\\": [\\n    {\\n      \\\"file\\\": \\\"backend/api.py\\\",\\n      \\\"score\\\": 1.5,\\n      \\\"reasons\\\": [\\n        \\\"python_impact\\\",\\n        \\\"backend_route:/api/users\\\"\\n      ]\\n    },\\n    {\\n      \\\"file\\\": \\\"frontend/dashboard.js\\\",\\n      \\\"score\\\": 1.3,\\n      \\\"reasons\\\": [\\n        \\\"js_keyword_api\\\",\\n        \\\"frontend_calls:/api/users\\\"\\n      ]\\n    }\\n  ],\\n  \\\"selected_file_count\\\": 2,\\n  \\\"tokens_est\\\": 171,\\n  \\\"context_file\\\": \\\"/tmp/tmppuxdx00y/repo/.uacos/fullstack/latest_fullstack_context.md\\\"\\n}\\n\",\n      \"stderr\": \"rm_spreadsheet_runtime_on_startup.py\\\", line 26, in warm_spreadsheet_runtime_on_startup\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 785, in warm_spreadsheet_runtime\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 720, in _warm_feature_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\\\", line 704, in _warm_collaboration_flows\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\\\", line 35986, in hydrate_crdt_from_proto\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\\\", line 747, in __call__\\n  File \\\"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\\\", line 150, in call\\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\\n\"\n    }\n  ]\n}\n",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  },
  "help": {
    "returncode": 0,
    "stdout_head": "usage: uacos [-h]\n             {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,llm-config,llm-enable,llm-disable,llm-run,context-compress,skill-plan,skill-execute,skill-execute-best,skill-exec-history,skill-exec-summary,feedback-ingest-execution,feedback-ingest-autopilot,feedback-summary,feedback-skill-score,feedback-recommend,feedback-events,ast-scan,graph-build,graph-query,graph-related,impact,context-smart,patch20-parse,patch20-validate,patch20-apply,patch20-rollback,provider-health,llm-run-hardened,provider-summary,provider-history,model-route-set,model-route-test,token-estimate,redact-test,budget-classify,summary-cache,context-budget,budget-report,vscode-pro-init,vscode-pro-check,openclaw-init,openclaw-config,openclaw-validate,openclaw-health,openclaw-prompt,openclaw-run,openclaw-history,openclaw-summary,prod-metrics,prod-report,prod-dashboard,prod-doctor,prod-serve,compress-cache,project-summary,context-compressed,compression-report,tx-begin,tx-run,tx-rollback,tx-status,tx-list,tx-report,runtime-init,runtime-config,runtime-validate,runtime-status,job-create,job-run-once,job-list,job-status,job-report,realrun-preflight,mock-provider-e2e,runtime-mock-e2e,ollama-realrun-check,openclaw-realrun-check,phase30-validate,mcp-serve,mcp-self-test,mcp-call,js-ts-scan,fullstack-index,fullstack-impact,fullstack-context} ...\n\nUniversal AI Context OS v3.7 - Phase 32 JS TS Full-stack Impact\n\npositional arguments:\n  {init,scan,search,symbols,snippets,repomap,context,stats,security-scan,patch-check,command-check,agent-init,agent-list,task-create,task-plan,workflow-run,evidence-report,adapter-init,adapter-list,adapter-export,adapter-run,mcp-manifest,artifact-ingest,extract-diff,test-run,token-log,token-summary,failed-memory,evidence-v2,apply-patch,rollback,done-gate,manifest-list,memory-add,memory-list,memory-search,memory-invalidate,regression-rule-add,regression-check,context-memory,dashboard,ops-summary,bootstrap,health,doctor,backup,export,import,release-check,write-run-scripts,write-systemd,skill-add,skill-list,skill-search,skill-suggest,skill-extract,skill-approve,skill-reject,skill-deprecate,skill-use,skill-review,context-skills,vscode-init,vscode-extension-skeleton,vscode-workspace,learn-from-evidence,learn-from-failure,learn-from-manifest,learn-review,learn-summary,learn-event-list,semantic-index,semantic-search,semantic-skills,semantic-memories,semantic-context,autopilot-init,autopilot-plan,autopilot-run,autopilot-status,autopilot-report,llm-init,ll",
    "stderr": ""
  },
  "compile": {
    "returncode": 0,
    "stdout": "",
    "stderr": "Spreadsheet runtime warmup failed during python startup\nTraceback (most recent call last):\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py\", line 26, in warm_spreadsheet_runtime_on_startup\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 785, in warm_spreadsheet_runtime\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 720, in _warm_feature_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py\", line 704, in _warm_collaboration_flows\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py\", line 35986, in hydrate_crdt_from_proto\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py\", line 747, in __call__\n  File \"/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py\", line 150, in call\npresentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.\n"
  }
}
```

---

## Source: `V1_END_TO_END_VALIDATION_REPORT.md`

# UACOS v1 End-to-End Validation Report

```json
{
  "status": "pass_with_fix",
  "e2e_standalone": {
    "returncode": 0,
    "summary": {
      "status": "pass",
      "done_gate": "done",
      "artifact": "pass",
      "test": "pass",
      "release": "pass"
    }
  },
  "bug_found_and_fixed": {
    "bug": "FTS5 MATCH syntax error when task/search text contained characters like =, e.g. GATE=UP",
    "fix": "Quoted every user query token in uacos/search.py::_match_query before FTS5 MATCH."
  },
  "phase10_baseline": "Phase 10 package previously reported 24 passed in 25.11s.",
  "note": "E2E was executed with python -S to avoid unrelated environment site-package startup overhead in the sandbox."
}
```

---

## Source: `V2_END_TO_END_VALIDATION_REPORT.md`

# V2 E2E Validation

```json
{
  "e2e": {
    "returncode": 0,
    "stdout": "V2_E2E_OK\nstatus= done\n",
    "stderr": ""
  },
  "help": {
    "returncode": 0,
    "has_autopilot": true
  }
}
```
