"""Validate teaching notebooks without importing PyTorch or executing training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_notebook(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"{path}: invalid JSON: {exc}"]

    if not isinstance(data, dict) or data.get("nbformat") != 4:
        return [f"{path}: expected Jupyter notebook format version 4"]
    cells = data.get("cells")
    if not isinstance(cells, list) or not cells:
        return [f"{path}: missing notebook cells"]
    executable = 0
    for i, cell in enumerate(cells):
        if not isinstance(cell, dict):
            errors.append(f"{path}: cells[{i}] is not an object")
            continue
        if cell.get("cell_type") not in {"markdown", "code", "raw"}:
            errors.append(f"{path}: cells[{i}] has unknown cell_type")
        if cell.get("cell_type") == "code":
            executable += 1
        source = cell.get("source")
        if not isinstance(source, str) and not (
            isinstance(source, list) and all(isinstance(s, str) for s in source)
        ):
            errors.append(f"{path}: cells[{i}] has invalid source")
    if not executable:
        errors.append(f"{path}: no executable teaching cells")
    return errors


def check_root(root: Path) -> tuple[int, list[str]]:
    notebooks = sorted((root / "notebooks").rglob("*.ipynb"))
    if not notebooks:
        return 0, [f"{root}: no notebooks discovered"]
    findings = [issue for nb in notebooks for issue in validate_notebook(nb)]
    return len(notebooks), findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    count, findings = check_root(args.root)
    for issue in findings:
        print("ERROR:", issue)
    print(f"Checked {count} notebooks; {len(findings)} error(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
