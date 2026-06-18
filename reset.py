#!/usr/bin/env python3
"""Reset the project to its red/unbuilt state so you can run the loop again."""
from pathlib import Path
import re

repo = Path(__file__).resolve().parent
(repo / "src" / "greeter.py").write_text(
    '"""The module under construction (reset to broken)."""\n\n\n'
    'def greet(name=None, shout=False):\n'
    '    raise NotImplementedError("the loop hasn\'t built this yet")\n',
    encoding="utf-8",
)
s = (repo / "STATUS.md").read_text(encoding="utf-8")
s = s.replace("- [x] ", "- [ ] ")
s = re.split(r"## Log", s)[0] + "## Log\n(empty — the loop appends here)\n"
(repo / "STATUS.md").write_text(s, encoding="utf-8")
print("reset: greeter stubbed, STATUS cleared")
