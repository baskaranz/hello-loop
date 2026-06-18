"""agent.py — the ACT step of the loop.

The loop calls one of these to make the next change. Every implementation is
*stateless*: it gets a fresh process / clean context each pass and decides what
to do only from what it reads on disk (SPEC.md, STATUS.md, the current source).
That clean-slate-each-pass property is the core Ralph-technique insight.

Three backends:
  - mock  : deterministic, offline, zero-cost. Used by default so the loop runs
            anywhere with no API key. Demonstrates the mechanics.
  - claude: shells out to Claude Code in print mode (`claude -p ...`).
  - api   : calls the Anthropic Messages API directly.

Only `mock` is exercised by the test run shipped with this project; the other
two are written to show exactly where a *real* agent slots into the same loop.
"""
from __future__ import annotations
import os
import re
import subprocess
from pathlib import Path

GREETER = Path("src/greeter.py")

# Four cumulative implementations. Version k makes tasks T1..T(k+1) pass.
# A real agent would *write* this code itself; the mock just knows the answer
# so the demo is deterministic.
_VERSIONS = [
    # after T1
    '''def greet(name=None, shout=False):
    return "Hello, World!"
''',
    # after T2
    '''def greet(name=None, shout=False):
    if name is None:
        name = "World"
    return f"Hello, {name}!"
''',
    # after T3
    '''def greet(name=None, shout=False):
    if name is None or not str(name).strip():
        name = "World"
    return f"Hello, {name}!"
''',
    # after T4
    '''def greet(name=None, shout=False):
    if name is None or not str(name).strip():
        name = "World"
    msg = f"Hello, {name}!"
    return msg.upper() if shout else msg
''',
]


def _tasks_done_from_status(status_path: Path) -> int:
    """Read how many tasks are already checked off — from disk, not memory."""
    text = status_path.read_text(encoding="utf-8")
    return len(re.findall(r"^- \[x\] ", text, flags=re.MULTILINE))


def mock_act(repo: Path, next_task: str) -> str:
    """Implement exactly one more task by rewriting src/greeter.py."""
    done = _tasks_done_from_status(repo / "STATUS.md")
    version = _VERSIONS[min(done, len(_VERSIONS) - 1)]
    (repo / GREETER).write_text(version, encoding="utf-8")
    return f"wrote src/greeter.py implementing {next_task}"


def claude_act(repo: Path, next_task: str) -> str:
    """Hand the next task to Claude Code in print mode. Requires `claude` on PATH."""
    spec = (repo / "SPEC.md").read_text(encoding="utf-8")
    prompt = (
        "You are inside an autonomous build loop. Implement EXACTLY ONE task, "
        "then stop.\n\n"
        f"Next task: {next_task}\n\n"
        f"Spec / acceptance criteria:\n{spec}\n\n"
        "Constraints: only edit src/greeter.py. Do not edit the tests. "
        "Make the change minimal and run nothing else."
    )
    subprocess.run(["claude", "-p", "--dangerously-skip-permissions", prompt], cwd=repo, check=True)
    return f"claude implemented {next_task}"


def api_act(repo: Path, next_task: str) -> str:
    """Call the Anthropic Messages API to write the next version of greeter.py."""
    import anthropic  # pip install anthropic ; needs ANTHROPIC_API_KEY

    client = anthropic.Anthropic()
    spec = (repo / "SPEC.md").read_text(encoding="utf-8")
    current = (repo / GREETER).read_text(encoding="utf-8")
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                "Return ONLY the full new contents of src/greeter.py (no prose, "
                "no markdown fences) that implements one more task.\n\n"
                f"Task to add now: {next_task}\n\n"
                f"Spec:\n{spec}\n\nCurrent file:\n{current}"
            ),
        }],
    )
    code = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    code = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", code.strip())  # strip fences if any
    (repo / GREETER).write_text(code + "\n", encoding="utf-8")
    return f"api implemented {next_task}"


BACKENDS = {"mock": mock_act, "claude": claude_act, "api": api_act}


def act(repo: Path, next_task: str, backend: str = "mock") -> str:
    fn = BACKENDS.get(backend)
    if fn is None:
        raise ValueError(f"unknown agent backend: {backend!r}")
    return fn(repo, next_task)
