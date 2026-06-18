# STATUS — hello-loop
This file is the loop's memory. The agent forgets between passes; this file remembers.
Each pass the loop reads the next unchecked task, the agent implements it, the verifier
checks it, and the loop writes the result back here.

## Tasks
- [x] T1 greet() returns "Hello, World!"
- [x] T2 greet(name) returns "Hello, {name}!"
- [x] T3 empty/whitespace name falls back to "World"
- [x] T4 greet(name, shout=True) upper-cases and ends with "!"

## Log
- 23:50:13 pass 1: T1 implemented and verified
- 23:50:25 pass 2: T2 implemented and verified
- 23:50:39 pass 3: T3 implemented and verified
- 23:50:57 pass 4: T4 implemented and verified
