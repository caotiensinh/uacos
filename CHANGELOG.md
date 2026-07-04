# Changelog

## 4.1.0b3

- Impact-aware planning: `build_context_pack()` (used by every adapter and by
  `autopilot_run`/`autopilot_plan`) now includes a graph-based "Impact
  Analysis" ranking (`impact_by_task`) alongside keyword search — previously
  only Auto Mode's compression path used it. `autopilot_plan()` now
  auto-suggests `allowed_files` from that ranking when the caller doesn't
  specify any; explicit caller-supplied scope still takes full precedence.
  If impact analysis finds nothing and no scope was given, the task is now
  explicitly flagged `allowed_files_source: "none_determined_scope_open"`
  with a `scope_warning` instead of silently proceeding with an
  unrestricted-scope task (patch_gate treats empty allowed_files/allowed_dirs
  as "no restriction").
- Added `impact_alignment_check()` / `uacos impact-alignment-check`: compares
  a patch's changed files against the task's impact ranking and warns
  (never blocks — it's a heuristic, not a hard safety boundary) on files the
  ranking didn't predict. Wired into `autopilot_run` as an informational
  step.
- Tightened the prompt sent to every adapter (`manual_chat`, CLI adapters,
  `ollama_openai`): explicit instructions to make the minimal change needed,
  avoid unrelated refactors, and keep responses terse — previously the
  prompt only said "stay in scope" and "return a diff."
- **Security fix**: `uacos/transaction/engine.py`'s `run_transaction()` — a
  third, separate patch-apply implementation alongside
  `apply_patch_with_backup` — validated patches via
  `uacos.patching.engine.validate_patch`, which has no secret scanning at
  all. A patch adding a real-shaped AWS key committed successfully and wrote
  the key to disk; the same patch through `apply_patch_with_backup` was
  correctly blocked. Fixed by scanning added lines for secrets before any
  apply, reusing the same detector `patch_gate.py` uses. This path has no
  CLI entry point yet (only `tx-list`/`list_transactions` is wired), so it
  was not exploitable through any shipped command, but was a live footgun
  for whoever wires it up next.
- **Fixed skill-import/export/publish/pull actually reaching the real skill
  pipeline.** `uacos/skill35.py`'s own module docstring states these
  commands "must not implement a separate skill engine" and must "route to
  the official skill store" — the code violated this silently: imported
  skills were written only to `.uacos/skill35/` (a separate local store),
  while the response falsely claimed `"source": "uacos.skill.store"`
  regardless of where data actually went. Skills imported via the
  documented CLI workflow never reached `suggest_skills()` /
  `skill_summary_for_task()` — the functions every adapter prompt and the
  MCP server's `get_memory`/`get_context` tools actually read. Fixed
  `export_skills`/`import_skills`/`publish_to_hub`/`pull_from_hub` to
  genuinely call `uacos.skill.store`'s `read_skills`/`add_skill` (old
  `task`/`response`-shaped export files are auto-mapped to the current
  schema). Left Auto Mode's separate experience-recall functions
  (`save`/`match`/`list_skills`/`stats`/`doctor`) untouched — different,
  already-working feature.
- Added `uacos vscode-init`/`vscode-extension` real-usage tests,
  `tests/test_impact_aware_planning.py`,
  `tests/test_multi_file_patch_rollback.py`,
  `tests/test_skill_import_reaches_official_store.py`. All fixes above were
  found and confirmed by actually running the affected code path end to
  end (real repo, real patch, real CLI/MCP calls) before and after the
  fix, not by code review alone.

## 4.1.0b2

- Fixed `uacos dashboard`: the command was referenced by the generated
  VSCode task, systemd unit, and desktop launcher scripts but was never
  registered in the CLI, so it silently fell through to the free-text LLM
  task runner instead of opening the dashboard.
- Added `uacos vscode-init` and `uacos vscode-extension` to actually
  generate the `.vscode/` integration files and the extension skeleton
  from the CLI (the generator code existed but had no CLI entry point).
- Fixed the "pro" VSCode extension (`uacos/ide/vscode_pro.py`), which
  referenced 10 CLI commands that never existed. Added the missing
  commands (`scan`, `context`, `skill-suggest`, `patch-check`,
  `patch20-validate`, `semantic-index`, `context-budget`,
  `feedback-recommend`, `autopilot-plan`, `autopilot-status`) and
  remapped stale references to their real equivalents.
- Added `tests/test_ide_extension_cli_wiring.py`, which asserts every
  command referenced by a generated VSCode extension actually exists in
  the CLI, to prevent this class of drift recurring silently.
- Added Autopilot Mode (`uacos autopilot-run`, `uacos autopilot-loop`):
  wires the existing patch-apply pipeline (patch-scope validation,
  checkpoint, apply, test, auto-rollback) to the CLI, plus a bounded
  retry loop that stops on success or after `--max-iterations`. Opt-in
  only (`--yes` required); refuses to loop with the `manual_chat`
  adapter, which cannot make unattended progress. See
  `docs/AUTOPILOT_MODE.md`.
- Fixed `scripts/release_gate.py`'s `install_smoke_test` check, which
  invoked its script with plain `sh` (dash on Ubuntu CI, rejects
  `set -o pipefail`) instead of the `bash` the script's shebang requires.
- Added multi-file patch integration tests
  (`tests/test_multi_file_patch_rollback.py`) covering apply, auto-rollback
  on test failure, and manual rollback for diffs touching more than one
  file — previously only single-file patches were covered.
- First public release: MIT `LICENSE`, `.gitignore`, GitHub issue
  templates, and a GitHub Pages docs site.

## 4.1.0b1

- Added Auto Mode for non-CLI users.
- Added `uacos init` and `uacos auto-install`.
- Added token/performance benchmark reports.
- Added release gate covering compile, pytest, self-check, and performance benchmark.
- Consolidated documentation into a smaller public-facing docs set.
- Added MCP endpoint tests and cache correctness tests.
- Improved Python 3.9 compatibility.
