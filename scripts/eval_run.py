from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "eval_report.json"


def _setup_import_path() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ["PYTHONPATH"] = root + os.pathsep + os.environ.get("PYTHONPATH", "")


def _contains_any(text: str, keywords: list[str]) -> bool:
    low = (text or "").lower()
    return any(str(word).lower() in low for word in keywords)


def _is_within_string_literal(text: str, pos: int, length: int) -> bool:
    quote_char = None
    i = pos - 1
    while i >= 0:
        c = text[i]
        if c in ('"', "'"):
            backslashes = 0
            j = i - 1
            while j >= 0 and text[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                quote_char = c
                break
        i -= 1
    if quote_char is None:
        return False

    end = pos + length
    j = end
    while j < len(text):
        c = text[j]
        if c == quote_char:
            backslashes = 0
            k = j - 1
            while k >= 0 and text[k] == "\\":
                backslashes += 1
                k -= 1
            if backslashes % 2 == 0:
                return True
        j += 1
    return False


def _is_dangerous_occurrence(text: str, banned: str) -> bool:
    low = (text or "").lower()
    banned_lower = str(banned).lower()
    start = 0
    while True:
        pos = low.find(banned_lower, start)
        if pos == -1:
            return False
        if not _is_within_string_literal(text, pos, len(banned_lower)):
            return True
        start = pos + len(banned_lower)
    return False


def _contains_none(text: str, words: list[str]) -> bool:
    if not text:
        return True
    for word in words:
        banned = str(word)
        if banned.lower() not in text.lower():
            continue
        if _is_dangerous_occurrence(text, banned):
            return False
    return True


def _strip_test_file_sections(text: str, selected_files: list[dict]) -> str:
    test_paths = {
        item.get("file", "")
        for item in selected_files
        if item.get("file")
        and re.search(r"(?:^|.*/)test_.*\.py$|(?:^|.*/).*_test\.py$", item["file"])
    }
    if not test_paths:
        return text

    out_lines = []
    skip = False
    for line in text.splitlines():
        if line.startswith("### "):
            file_path = line[4:].strip()
            skip = file_path in test_paths
            if skip:
                continue
        if not skip:
            out_lines.append(line)
    return "\n".join(out_lines)


def run_eval(repo_root: Path, golden_file: Path, real: bool = False) -> dict:
    from uacos.compression.engine import compressed_context
    from uacos.runtime.llm33_runner import llm_run_real

    tasks = json.loads(golden_file.read_text(encoding="utf-8"))
    results = []
    failed = []
    for index, item in enumerate(tasks):
        task = item["task"]
        expected = item.get("expected_keywords", [])
        banned = item.get("must_not_contain", [])
        if real:
            response = llm_run_real(repo_root, task, size="small", real=True)
            text = json.dumps(response, ensure_ascii=False)
            mode_status = response.get("status")
        else:
            ctx = compressed_context(repo_root, task, max_tokens=3000, max_files=4, refresh_cache=(index == 0))
            text = ctx.get("content", "")
            text = _strip_test_file_sections(text, ctx.get("selected_files", []))
            mode_status = ctx.get("status", "ok")
        has_expected = _contains_any(text, expected)
        has_no_banned = _contains_none(text, banned)
        ok = bool(has_expected and has_no_banned)
        row = {
            "task": task,
            "ok": ok,
            "mode_status": mode_status,
            "expected_keywords": expected,
            "must_not_contain": banned,
            "has_expected_keyword": has_expected,
            "has_no_banned_words": has_no_banned,
        }
        results.append(row)
        if not ok:
            failed.append(row)
    pass_rate = round((len(results) - len(failed)) / max(1, len(results)), 4)
    return {
        "status": "pass" if pass_rate >= 0.80 else "fail",
        "mode": "real" if real else "dry",
        "task_count": len(results),
        "pass_rate": pass_rate,
        "failed_tasks": failed,
        "results": results,
    }


def main() -> int:
    _setup_import_path()
    parser = argparse.ArgumentParser(description="Run UACOS golden context/LLM evals.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--golden", default=str(ROOT / "evals" / "golden_tasks.json"))
    parser.add_argument("--real", action="store_true")
    args = parser.parse_args()

    report = run_eval(Path(args.repo).resolve(), Path(args.golden), real=args.real)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
