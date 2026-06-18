#!/usr/bin/env python3
"""loop.py — claudified: hand the loop to Claude Code as a goal.

The original hand-rolled PLAN/ACT/VERIFY/REMEMBER harness is replaced by a
single `claude -p` invocation. Claude Code handles tool use, file edits, test
runs, and STATUS.md updates itself — the same loop, zero harness code.

Run it:
    python3 loop.py                  # drive Claude Code (needs `claude` on PATH)
    python3 reset.py && python3 loop.py  # reset to broken state first
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

GOAL = """
You are running an autonomous build loop. Your goal:

  All tests in tests/ pass AND every task in STATUS.md is checked off.

Repeat until done:
  1. Read STATUS.md — find the next unchecked task  (- [ ] Tx ...)
  2. Read SPEC.md — understand the acceptance criteria
  3. Edit src/greeter.py to implement that task (only this file)
  4. Run: python3 -m unittest discover -s tests -q
  5. If green: update STATUS.md — mark the task done (- [ ] → - [x])
  6. If red: fix src/greeter.py and re-run tests before moving on
  7. Stop when all tasks are checked off and the full suite is green

Constraints:
  - Only edit src/greeter.py
  - Do not edit the tests
  - Do not stop early — loop until the stop condition is provably met
"""

if __name__ == "__main__":
    sys.exit(subprocess.run(
        ["claude", "-p", "--dangerously-skip-permissions", GOAL.strip()],
        cwd=REPO,
    ).returncode)
