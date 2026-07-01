# Changelog

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
