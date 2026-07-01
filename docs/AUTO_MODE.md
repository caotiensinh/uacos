# UACOS Auto Mode

Auto Mode is for users who do not want to remember CLI sequences.

## What It Does

`uacos auto` prepares a repository by running the normal UACOS production workflow automatically:

- bootstrap local UACOS state
- health check
- graph build
- compression cache build
- compressed task context preparation
- cache status
- skill status
- budget status
- optional MCP self-test
- optional lightweight performance/token probe

It writes:

```text
reports/uacos_auto_report.json
.uacos/auto/auto_state.json
```

## Friendly Launcher

Advanced users can run:

```bash
uacos auto-install --repo .
```

This creates:

```text
UACOS_AUTO_START.py
```

Non-CLI users can run that file from the project root to let UACOS prepare itself.

## Watch Mode

```bash
uacos auto --repo . --watch --interval 10
```

Watch mode polls source and documentation files. When they change, UACOS refreshes the repo state.

## Safety

Auto Mode does not enable real LLM runs, apply patches, or create releases by itself. It prepares context, cache, graph, reports, and health evidence so both CLI and non-CLI users get the same baseline performance.

## Dogfood And Learning Loop

For this repo, run Auto Mode after each upgrade so UACOS measures its own impact immediately:

```bash
python -m uacos.cli auto --repo . --summary
python scripts/uacos_performance_benchmark.py --repo . --summary
python scripts/release_gate.py
```

Auto Mode now recalls relevant project memory and reusable skills before building compressed context. After a run, it records a compact dogfood lesson into `.uacos/memory.jsonl` and `.uacos/skill35/` so later sessions can reuse the same operating pattern.

This is not hidden model training. It is repository-local memory and skill retrieval: UACOS stores concise lessons, recalls matching lessons for new tasks, and keeps full reports in `reports/` while terminal output stays short with `--summary`.

Useful checks:

```bash
python -m uacos.cli experience-recall --repo . --task "optimize token usage"
python -m uacos.cli learn-summary --repo .
python -m uacos.cli skill35-status --repo .
```

[project]
name = "uacos"
version = "4.1.0b1"
description = "Local-first code intelligence, auto context, cache, MCP, and release-gate tooling for software projects."
readme = "README.md"
license = "MIT"
requires-python = ">=3.9"

MIT License

Copyright (c) 2026 UACOS maintainers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
