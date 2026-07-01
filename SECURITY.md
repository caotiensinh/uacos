# Security Policy

## Supported Version

The current supported public beta line is `4.1.0-beta`.

## Safety Defaults

- Auto Mode does not apply patches.
- Auto Mode does not create releases.
- Real LLM execution requires explicit CLI/config action.
- MCP server is localhost-only by default.
- Release artifacts must not be created when `scripts/release_gate.py` fails.

## Reporting Issues

Report security issues privately to the project maintainers. Include reproduction steps, affected commands, and expected impact.
