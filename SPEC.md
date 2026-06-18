# SPEC — hello-loop

## Goal (the stop condition, stated as a contract)
A `greet()` function exists and every acceptance test is green.

| Contract field | Value |
|---|---|
| **End state** | All four acceptance scenarios pass |
| **Evidence**  | `python -m unittest` exits 0 for each task's test |
| **Constraints** | Only edit `src/greeter.py`. Don't touch the tests. |
| **Budget** | Stop after 8 passes, whichever comes first |

## Acceptance scenarios (GIVEN / WHEN / THEN)
- **T1** — GIVEN no name, WHEN I call `greet()`, THEN it returns `"Hello, World!"`
- **T2** — GIVEN a name, WHEN I call `greet("Baskaran")`, THEN it returns `"Hello, Baskaran!"`
- **T3** — GIVEN an empty or whitespace name, WHEN I call `greet("   ")`, THEN it falls back to `"Hello, World!"`
- **T4** — GIVEN `shout=True`, WHEN I call `greet("ada", shout=True)`, THEN it returns `"HELLO, ADA!"`

The verifier (the test suite) is the single source of truth for "done".
