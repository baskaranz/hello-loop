# Using the Loop Approach in Your Codebase

The loop approach lets Claude autonomously work through a task list, verifying each step against your test suite, until everything is green — without you prompting each turn.

---

## The three things you need

| Thing | What it is | Example in this repo |
|---|---|---|
| **Goal / contract** | The verifiable stop condition | `SPEC.md` |
| **Task queue** | A checklist on disk Claude reads and updates | `STATUS.md` |
| **Loop script** | Hands the goal to Claude and lets it run | `loop.py` |

---

## Step 1 — Write your task queue

Create a `STATUS.md` at your repo root. Break your work into small, independently verifiable tasks:

```markdown
## Tasks
- [ ] T1 add input validation to UserService
- [ ] T2 return 400 for missing required fields
- [ ] T3 write unit tests for the validation logic
- [ ] T4 update the API docs

## Log
(empty — the loop appends here)
```

Keep each task small enough that one Claude pass can implement and verify it.

---

## Step 2 — Write your goal

Create a `SPEC.md` (or inline it in your loop script). Be explicit about:
- the end state
- how to verify it (your test command)
- what files Claude is allowed to touch

```markdown
## Goal
All input validation is implemented and the test suite is green.

## Evidence
`pytest tests/` exits 0

## Constraints
Only edit files under `src/`. Do not edit tests.
```

---

## Step 3 — Create the loop script

Copy this `loop.py` to your repo and adjust the `GOAL` and test command:

```python
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

GOAL = """
You are running an autonomous build loop. Your goal:

  All tasks in STATUS.md are checked off AND the test suite is green.

Repeat until done:
  1. Read STATUS.md — find the next unchecked task (- [ ] Tx ...)
  2. Read SPEC.md — understand the acceptance criteria
  3. Implement the task (only edit files listed in SPEC.md constraints)
  4. Run: pytest tests/          # <-- change to your test command
  5. If green: mark the task done in STATUS.md (- [ ] → - [x])
  6. If red: fix the code and re-run before moving on
  7. Stop when all tasks are checked off and the full suite is green

Do not stop early. Loop until the stop condition is provably met.
"""

if __name__ == "__main__":
    sys.exit(subprocess.run(
        ["claude", "-p", "--allowedTools", "Read,Edit,Write,Bash,Glob"],
        input=GOAL.strip(), text=True, cwd=REPO,
    ).returncode)
```

---

## Step 4 — Run it

```bash
python3 loop.py
```

Watch Claude work through each task, run your tests, and check off the queue.

To start over:
```bash
# reset STATUS.md manually or write a reset.py like this repo's
python3 reset.py && python3 loop.py
```

---

## Two principles that make it work

**1. State lives on disk, not in context.**
Claude re-reads `STATUS.md` at the start of each task. It forgets between passes; the file remembers. This is the *Ralph technique* — clean context reading current reality.

**2. The writer never grades its own work.**
Your existing test suite is the verifier. Claude doesn't decide when a task is done — the tests do. Never let the agent self-report success without an external check.

---

## Tips

- **Small tasks win.** One task = one function, one endpoint, one edge case. Big tasks stall loops.
- **Test command must be deterministic.** Flaky tests break the loop. Fix flakiness before looping.
- **Constrain the blast radius.** The tighter your `Constraints` field, the less Claude can accidentally break.
- **Add a budget if you want a guardrail.** Track pass count in your loop script and halt after N passes if the suite is still red.
- **`--allowedTools` scopes the blast radius.** Only grant the tools the loop actually needs (`Read,Edit,Write,Bash,Glob`). This runs non-interactively without bypassing all permissions.
