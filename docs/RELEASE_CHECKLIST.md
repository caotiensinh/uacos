# Release Checklist

Run these commands from the repo root:

```bash
python -m compileall -q uacos
python scripts/uacos_self_check.py
python scripts/community_readiness_check.py
python scripts/release_gate.py
```

Do not create a release package or tag if `scripts/release_gate.py` fails.
