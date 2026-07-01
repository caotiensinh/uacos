from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import argparse
import shutil
import tempfile
import zipfile
import re

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TOP_LEVEL = [
    "uacos",
    "tests",
    "scripts",
    "docs",
    "evals",
    "pyproject.toml",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "UACOS_AUTO_START.py",
]


def parse_version_from_pyproject(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    project_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            project_section = stripped == "[project]"
            continue
        if project_section and stripped.startswith("version"):
            match = re.search(r"^version\s*=\s*['\"]([^'\"]+)['\"]", stripped)
            if match:
                return match.group(1)
    raise ValueError("Could not read project.version from pyproject.toml")


def clean_copy(src_root: Path, dest_root: Path) -> None:
    missing = [name for name in ALLOWED_TOP_LEVEL if not (src_root / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required release source path(s): {', '.join(missing)}")

    for name in ALLOWED_TOP_LEVEL:
        src = src_root / name
        dest = dest_root / name
        if src.is_dir():
            shutil.copytree(
                src,
                dest,
                symlinks=False,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        elif src.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)


def remove_pycache_and_pyc(root: Path) -> tuple[int, int]:
    removed_dirs = 0
    removed_files = 0
    for path in sorted(root.rglob("__pycache__"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            removed_dirs += 1
    for path in root.rglob("*.pyc"):
        if path.is_file():
            path.unlink()
            removed_files += 1
    return removed_dirs, removed_files


def build_zip(src_root: Path, output: Path) -> tuple[int, int]:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src_root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(src_root).as_posix()
            zf.write(path, rel)
            count += 1
    size = output.stat().st_size
    return count, size


def verify_zip(output: Path) -> tuple[int, str]:
    if not output.exists():
        raise FileNotFoundError(f"Release zip not found: {output}")
    with zipfile.ZipFile(output, "r") as zf:
        entries = zf.namelist()
    if len(entries) >= 300:
        raise AssertionError(f"Zip entry count too large: {len(entries)}")
    if "uacos/cli.py" not in entries:
        raise AssertionError("Missing required entry: uacos/cli.py")
    if "pyproject.toml" not in entries:
        raise AssertionError("Missing required entry: pyproject.toml")
    for name in entries:
        if name.startswith(".uacos/"):
            raise AssertionError(f"Unexpected internal path in archive: {name}")
        if name.startswith("reports/"):
            raise AssertionError(f"Unexpected internal path in archive: {name}")
        if name.startswith("missing-repo/"):
            raise AssertionError(f"Unexpected internal path in archive: {name}")
        if ".egg-info" in name:
            raise AssertionError(f"Unexpected egg-info path in archive: {name}")
        if "__pycache__" in name:
            raise AssertionError(f"Unexpected __pycache__ entry in archive: {name}")
        if name.endswith(".pyc"):
            raise AssertionError(f"Unexpected .pyc entry in archive: {name}")
    digest = sha256(output.read_bytes()).hexdigest()
    return len(entries), digest


def get_default_output(version: str) -> Path:
    return ROOT / "reports" / f"uacos_v{version}_release.zip"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a clean UACOS release zip from a white-listed source tree.")
    parser.add_argument("--repo", default=".", help="Source repository root")
    parser.add_argument("--output", default=None, help="Output zip file path")
    args = parser.parse_args()

    src_root = Path(args.repo).resolve()
    version = parse_version_from_pyproject(src_root / "pyproject.toml")
    output = Path(args.output) if args.output else get_default_output(version)

    with tempfile.TemporaryDirectory(prefix="uacos_release_") as tmpdir:
        temp_root = Path(tmpdir) / f"uacos_v{version}_release"
        temp_root.mkdir(parents=True, exist_ok=True)
        clean_copy(src_root, temp_root)
        removed_dirs, removed_files = remove_pycache_and_pyc(temp_root)
        file_count, zip_size = build_zip(temp_root, output)

    entry_count, digest = verify_zip(output)

    print(f"version: {version}")
    print(f"output: {output}")
    print(f"entries: {entry_count}")
    print(f"zip_size: {zip_size}")
    print(f"sha256: {digest}")
    print(f"removed_pycache_dirs: {removed_dirs}")
    print(f"removed_pyc_files: {removed_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
