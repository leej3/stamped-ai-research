#!/usr/bin/env python3
"""Keep literal captured pointer text out of git-annex's clean filter."""
from pathlib import Path
import json
import subprocess

path = Path(subprocess.check_output(
    ["git", "rev-parse", "--git-path", "info/attributes"], text=True).strip())
path.parent.mkdir(parents=True, exist_ok=True)
before = path.read_text() if path.exists() else ""
lines = ["receipts/** -filter", "hooks/** -filter"]
missing = [line for line in lines if line not in before.splitlines()]
if missing:
    path.write_text(before.rstrip("\n") + "\n" + "\n".join(missing) + "\n")
result = subprocess.check_output(
    ["git", "check-attr", "filter", "--", "receipts/example.stdout"], text=True).strip()
if not result.endswith(": unset"):
    raise SystemExit("Captured receipts still have an active filter: " + result)
print(json.dumps({"attributes_file": str(path), "added_lines": missing,
                  "filter_check": result, "scope": "shared by this repository's worktrees"}, indent=2))
