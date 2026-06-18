# hello-loop — loop engineering, demonstrated

A tiny, runnable project that shows what *loop engineering* actually is: you don't
prompt the agent turn by turn — you design a **harness** that prompts it for you,
against a goal, verifying each step, until the work is provably done.

The toy task: drive a `greet()` function from a **red** test suite to **green**,
one task at a time. No API key, no dependencies — just Python 3 standard library.

---

## Run it

```bash
cd hello-loop
python3 loop.py            # watch the loop turn red → green
python3 reset.py           # back to the broken state to run again
```

Sample output:

```
  ── pass 1 ─────────────────────────────
  PLAN     next unchecked task → T1 greet() returns "Hello, World!"
  ACT      wrote src/greeter.py implementing T1 ...
  VERIFY   T1 test → PASS
  REMEMBER checked off T1 in STATUS.md
  ...
  ✓ STOP — all tasks green in 4 passes. Stop condition met.
```

Try the guardrail: `python3 loop.py --budget 2` halts at the budget ceiling
*without* finishing — a stop, not a win. That's the failure mode loops must design for.

---

## The loop

```
        ┌─────────────────────────────────────────────┐
        │                                             │
        ▼                                             │
   ┌─────────┐   ┌───────┐   ┌─────────┐   ┌──────────┐│
   │  PLAN   │──▶│  ACT  │──▶│ VERIFY  │──▶│ REMEMBER │┘
   │ read    │   │ fresh │   │ run the │   │ write    │
   │ STATUS  │   │ agent │   │ tests   │   │ STATUS   │
   └─────────┘   └───────┘   └─────────┘   └──────────┘
                                  │
                          all green? ──▶ ✓ STOP (success)
                          budget hit? ──▶ ■ STOP (guardrail)
```

You wrote that control structure once. You never prompted any individual pass.
That is the whole idea.

---

## What each file is (mapped to the building blocks)

| File | Role in the loop | Building block |
|---|---|---|
| `loop.py` | the harness: plan → act → verify → remember → stop | **Automation** (the heartbeat) + **stop condition** |
| `SPEC.md` | the goal stated as a contract: end state, evidence, constraints, budget | **the verifiable stop condition** |
| `STATUS.md` | the work queue + log; survives every reset | **Memory** (state on disk) |
| `agent.py` | the ACT step; **stateless** — decides only from disk each pass | the agent + **fresh context** (Ralph) |
| `tests/test_greeter.py` | the honest signal; separate from the maker | **Sub-agent / verifier** (maker ≠ checker) |
| `src/greeter.py` | the code under construction | the work product |

Two principles to notice in the code:

1. **State lives on disk, not in the process.** `agent.py` re-reads `STATUS.md`
   every pass to decide what to do. The agent forgets; the repo remembers. That's
   the Ralph technique — a clean context each pass, reading current reality.
2. **The writer never grades its own work.** `verify()` runs the test suite as a
   separate step. "Done" is a claim the verifier has to confirm, not something the
   agent asserts.

---

## Swap in a real agent

The mock agent just knows the answer so the demo is deterministic and free. The
*same loop* drives a real coding agent — only the ACT step changes:

```bash
python3 loop.py --agent claude   # shells out to `claude -p` (Claude Code on PATH)
python3 loop.py --agent api      # calls the Anthropic Messages API (ANTHROPIC_API_KEY)
```

See `agent.py` → `claude_act()` and `api_act()` for exactly where the real model
plugs in. Everything else — the plan/verify/remember/stop scaffolding — is unchanged.

### The same loop in Claude Code, natively

You wouldn't hand-roll `loop.py` in practice; Claude Code ships the primitives:

```bash
# run until a verifiable condition holds (the stop-condition contract)
/goal all tests in tests/ pass and STATUS.md has no unchecked tasks

# or schedule a recurring pass, each with its own fresh context
/loop 5m read STATUS.md, implement the next unchecked task, run the tests, check it off
```

`/goal` even applies the maker-checker split to the stop condition itself: a
separate model decides whether the loop is done, not the one that did the work.

---

## How does OpenSpec fit with loops?

Short answer: **OpenSpec doesn't *run* a loop — it produces the spec, state, and
memory a loop runs *on*.** They're complementary layers, and they slot together
almost exactly like the files in this project.

[OpenSpec](https://github.com/Fission-AI/OpenSpec) is a lightweight spec-driven
development framework (npm `@fission-ai/openspec`, tool-agnostic, no API key). Its
workflow is **Propose → Apply → Archive**:

- `/opsx:propose <idea>` creates a change folder with `proposal.md`, `specs/`
  (requirements as GIVEN/WHEN/THEN scenarios), `design.md`, and a `tasks.md` checklist.
- `/opsx:apply` implements the tasks one at a time, following that checklist.
- `/opsx:archive` folds the finished change into the living `openspec/specs/`
  (the source of truth) and records it.

Look at what those artifacts *are* in loop terms — it's the same anatomy as this repo:

| OpenSpec artifact | hello-loop equivalent | Loop role |
|---|---|---|
| `proposal.md` + `specs/` scenarios | `SPEC.md` | the **goal / contract** (verifiable end state) |
| `tasks.md` checklist | `STATUS.md` | the **work queue + memory** on disk |
| `/opsx:apply` (step through tasks) | the loop's ACT step | the agent doing one unit |
| `/opsx:verify` | `verify()` / the test suite | the **verification gate** |
| `/opsx:archive` → living specs | `mark_done()` writing STATUS | **memory** updated on success |
| `openspec/specs/` vs `openspec/changes/` | — | source-of-truth vs proposed (a maker/checker split at the artifact level) |

So OpenSpec gives a loop the two things it most needs and is easiest to get wrong:

- a **durable, reviewable goal** that doesn't live in chat history, and
- a **task checklist on disk** — exactly the "external state file the model can't
  pollute" that the Ralph technique depends on.

OpenSpec even recommends the same context hygiene a loop relies on ("clear your
context before implementation"), and its docs describe running `apply` across
isolated **git worktrees with sub-agents**, each running verify before merge —
which *is* loop engineering, with OpenSpec supplying the spec and state.

**Putting them together:** wrap OpenSpec's apply phase in a loop. Each pass reads
the next unchecked item in `tasks.md`, implements it, runs your tests plus
`/opsx:verify`, checks it off, and commits. The loop exits when `tasks.md` is fully
checked and verification passes — then `/opsx:archive`. OpenSpec is the *what* and
the *memory*; the loop is the *keep-going-until-done*. What OpenSpec does **not**
give you is the heartbeat (scheduling) or the autonomous control structure — that's
`/loop`, `/goal`, cron, or a harness like `loop.py`.

---

*Concepts: loop engineering (Addy Osmani, 2026), the Ralph technique (Geoffrey
Huntley). Claude Code `/loop` and `/goal`, and OpenSpec commands, verified against
their docs as of June 2026 — both move fast, so check before relying on specifics.*
