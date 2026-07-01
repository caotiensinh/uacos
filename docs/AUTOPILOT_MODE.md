# UACOS Autopilot Mode

Autopilot Mode is different from [Auto Mode](AUTO_MODE.md). Auto Mode only prepares
context, cache, graph, and reports — it never applies patches or calls a real LLM.
Autopilot Mode does apply patches automatically, in a bounded retry loop, and
requires explicit opt-in every time.

## What It Does

`uacos autopilot-loop` repeats this cycle up to `--max-iterations` times:

1. Build task context (`autopilot-plan`'s context pack)
2. Call the configured adapter to get a response (real local LLM via Ollama,
   or a CLI adapter such as Aider/OpenClaw)
3. Extract a patch from the response
4. Validate the patch against the task's file/dir scope
   (same gate as `uacos patch-check` / `security/patch_gate.py`)
5. Checkpoint the affected files, apply the patch
6. Run the task's tests
7. If tests fail, roll back automatically (same rollback used by
   `uacos.apply.patch_apply`) and try again on the next iteration
8. Stop as soon as one iteration reports `done`, or after `max-iterations`
   is exhausted

None of these gates can be skipped by Autopilot Mode — it reuses the same
`patch_gate`/secret-scan/rollback code paths as manual patch application.

## Safety

- `autopilot-loop` requires `--yes`. Without it, the command refuses to run
  and explains why.
- `autopilot-loop` refuses to run with the `manual_chat` adapter — that
  adapter exports a prompt for a human to paste into a chat UI and cannot
  produce a response unattended, so a loop built on it can never make
  progress on its own.
- Every patch still goes through the same scope allowlist and secret scan as
  a manually-applied patch. There is no separate, looser code path for
  autopilot-applied changes.
- A single manual pass (`autopilot-plan` + `autopilot-run`) is available if
  you want one iteration under your control instead of a loop — `autopilot-run
  --apply` also requires `--yes`.

## Usage

Single manual pass (plan, then run once, review before applying):

```bash
python -m uacos.cli autopilot-plan --repo . --title "Fix login bug" --objective "Fix the login redirect bug" --allowed-file app/auth.py --test "pytest -q"
python -m uacos.cli autopilot-run --repo . --task-file .uacos/tasks/TASK-xxxx.json --adapter ollama_openai --apply --yes
```

Bounded automatic loop (up to 3 tries, requires a real adapter and `--yes`):

```bash
python -m uacos.cli autopilot-loop --repo . \
  --title "Fix login bug" \
  --objective "Fix the login redirect bug" \
  --allowed-file app/auth.py \
  --test "pytest -q" \
  --adapter ollama_openai \
  --max-iterations 3 \
  --yes
```

Check status of past runs:

```bash
python -m uacos.cli autopilot-status --repo .
```

## Reports

Each iteration is saved as `.uacos/autopilot_runs/AUTO-*.json`. `autopilot-loop`
returns a summary with `status` (`done` or `exhausted`), `iterations_used`, and
one entry per attempt with its run ID and outcome.
