import re
from pathlib import Path

from uacos.cli import KNOWN_COMMANDS
from uacos.ide.vscode import build_extension_js
from uacos.ide.vscode_pro import write_vscode_pro_extension, validate_vscode_pro_extension

def _referenced_cli_commands(js_text: str) -> set[str]:
    found = set()
    for line in js_text.splitlines():
        m = re.search(r"run(?:In)?Terminal\([^,]+,\s*'([a-z0-9-]+)\s", line)
        if not m:
            m = re.search(r"runCapture\('([a-z0-9-]+)\s", line)
        if m:
            found.add(m.group(1))
    return found


def test_basic_vscode_extension_only_calls_real_commands():
    js = build_extension_js()
    referenced = _referenced_cli_commands(js)
    assert referenced, "expected to find at least one referenced command"
    missing = referenced - KNOWN_COMMANDS
    assert not missing, f"basic VSCode extension references non-existent CLI commands: {missing}"


def test_pro_vscode_extension_only_calls_real_commands(tmp_path: Path):
    output = tmp_path / "vscode-uacos-pro"
    result = write_vscode_pro_extension(output, overwrite=True)
    assert result["status"] == "ok"

    validation = validate_vscode_pro_extension(output)
    assert validation["status"] == "pass", validation["findings"]

    js = (output / "extension.js").read_text(encoding="utf-8")
    referenced = _referenced_cli_commands(js)
    assert referenced, "expected to find at least one referenced command"
    missing = referenced - KNOWN_COMMANDS
    assert not missing, f"pro VSCode extension references non-existent CLI commands: {missing}"
