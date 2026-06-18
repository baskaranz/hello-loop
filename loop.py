#!/usr/bin/env python3
"""loop.py — the loop-engineering harness (the whole point of this project).

You do not prompt the agent. You design THIS, and let it drive the agent:

    while not done:
        PLAN     read STATUS.md, pick the next unchecked task
        ACT      a fresh, stateless agent implements that one task
        VERIFY   run the test suite — the honest, separate source of truth
        REMEMBER write the result back to STATUS.md (memory on disk)
        STOP?    all tasks green  -> success
                 budget exhausted -> guardrail halt (a stop, not a win)

Run it:
    python3 loop.py                 # default: offline mock agent
    python3 loop.py --agent claude  # drive Claude Code (needs `claude` on PATH)
    python3 loop.py --agent api     # drive the Anthropic API (needs ANTHROPIC_API_KEY)
    python3 loop.py --budget 4      # tighten the budget ceiling
"""
from __future__ import annotations
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import agent

REPO = Path(__file__).resolve().parent
STATUS = REPO / "STATUS.md"

# Map each task id to the test that proves it. The verifier is separate from the
# maker on purpose: the agent that writes code never gets to grade its own work.
TASK_TESTS = {
    "T1": "tests.test_greeter.TestGreeter.test_t1",
    "T2": "tests.test_greeter.TestGreeter.test_t2",
    "T3": "tests.test_greeter.TestGreeter.test_t3",
    "T4": "tests.test_greeter.TestGreeter.test_t4",
}

C = {"run": "\033[36m", "hu": "\033[33m", "ok": "\033[32m", "dim": "\033[2m", "x": "\033[0m"}


def color(s, k):
    return f"{C[k]}{s}{C['x']}" if sys.stdout.isatty() else s


def read_tasks():
    """Parse STATUS.md -> ordered list of (id, text, done?). State lives on disk."""
    tasks = []
    for line in STATUS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"- \[( |x)\] (T\d+) (.+)", line)
        if m:
            tasks.append({"id": m.group(2), "text": m.group(3), "done": m.group(1) == "x"})
    return tasks


def mark_done(task_id):
    """REMEMBER: check the task off in STATUS.md so the next pass picks up here."""
    out = []
    for line in STATUS.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"- [ ] {task_id} "):
            line = line.replace("- [ ] ", "- [x] ", 1)
        out.append(line)
    STATUS.write_text("\n".join(out) + "\n", encoding="utf-8")


def log(msg):
    text = STATUS.read_text(encoding="utf-8")
    stamp = dt.datetime.now().strftime("%H:%M:%S")
    if "(empty — the loop appends here)" in text:
        text = text.replace("(empty — the loop appends here)", f"- {stamp} {msg}")
    else:
        text = text.rstrip() + f"\n- {stamp} {msg}\n"
    STATUS.write_text(text, encoding="utf-8")


def verify(task_id) -> bool:
    """VERIFY: run just this task's test. exit 0 == provably done."""
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", TASK_TESTS[task_id]],
        cwd=REPO, capture_output=True, text=True,
    )
    return proc.returncode == 0


def suite_green() -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
        cwd=REPO, capture_output=True, text=True,
    )
    return proc.returncode == 0


def run(budget: int, backend: str):
    print(color("\n  loop engineering · hello-world\n", "run"))
    print(f"  agent backend : {backend}")
    print(f"  budget ceiling: {budget} passes")
    print(f"  stop condition: every task green  (verifier = the test suite)\n")

    for pass_n in range(1, budget + 1):
        tasks = read_tasks()
        nxt = next((t for t in tasks if not t["done"]), None)

        # STOP? success path — nothing left and the whole suite is green
        if nxt is None:
            if suite_green():
                print(color(f"  ✓ STOP — all tasks green in {pass_n - 1} passes. "
                            "Stop condition met.\n", "ok"))
                return 0
            # tasks checked but suite red: a real loop would re-open work here
            print(color("  suite regressed; re-opening verification\n", "hu"))

        print(color(f"  ── pass {pass_n} ─────────────────────────────", "dim"))
        # PLAN
        print(f"  {color('PLAN', 'run')}     next unchecked task → {nxt['id']} {nxt['text']}")
        # ACT  (fresh, stateless agent — clean context every pass)
        note = agent.act(REPO, f"{nxt['id']} {nxt['text']}", backend=backend)
        print(f"  {color('ACT', 'run')}      {note}")
        # VERIFY (separate from the maker)
        ok = verify(nxt["id"])
        if ok:
            print(f"  {color('VERIFY', 'run')}   {nxt['id']} test → {color('PASS', 'ok')}")
            mark_done(nxt["id"])                       # REMEMBER
            log(f"pass {pass_n}: {nxt['id']} implemented and verified")
            print(f"  {color('REMEMBER', 'run')} checked off {nxt['id']} in STATUS.md")
        else:
            print(f"  {color('VERIFY', 'run')}   {nxt['id']} test → {color('FAIL', 'hu')}"
                  f"  (signal feeds back; loop tries again)")
            log(f"pass {pass_n}: {nxt['id']} failed verification")
        print()

    # STOP? budget path — a guardrail, not a success
    print(color(f"  ■ STOP — budget ceiling ({budget} passes) hit without finishing. "
                "Guardrail, not a win.\n", "hu"))
    return 1


def main():
    ap = argparse.ArgumentParser(description="A hello-world loop-engineering harness.")
    ap.add_argument("--agent", default="mock", choices=["mock", "claude", "api"])
    ap.add_argument("--budget", type=int, default=8, help="max passes (the budget ceiling)")
    args = ap.parse_args()
    sys.exit(run(args.budget, args.agent))


if __name__ == "__main__":
    main()
