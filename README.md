# Bober

Lightweight agentic loop in under 200 lines of Python.

Write a program as a markdown file → Bober runs an AI agent on it in a loop.

Inspired by [snarktank/ralph](https://github.com/snarktank/ralph) and [karpathy/autoresearch](https://github.com/lemonodor/autoresearch).

## Install

```bash
uv tool install git+https://github.com/mobarski/bober
```

## Quick start

```bash
bober plan inbox/task1.md           # create execution plan → task1.md.out.md
bober pick inbox/task1.md 20        # run loop, max 20 iterations

bober plan inbox/task1.md --variant mk2   # named variant → task1.md.mk2.md
bober pick inbox/task1.md 20 --variant mk2
```

Example task file (`inbox/task1.md`):

```markdown
# Task
- create empty file "hello.py"
- write hello world program in this file
- execute it with uv
- log output to "output.txt"
```

## How it works

```
task.md ──→ bober plan ──→ task.md.out.md (execution plan)
              ↓
            bober pick ──→ agent loop (read → work → update)
              ↓
            stops when:
              • stopword in output (e.g. BREAK-THE-LOOP)
              • non-zero exit code
              • iteration limit reached
```

Each iteration: the agent reads the task, does work, updates progress in the output file.

## Unix-like I/O

| Concept | Bober equivalent |
|---|---|
| stdin | task file (your markdown program) |
| stdout | `.out.md` (execution output) |
| stderr | `.log.jsonl` (structured logs) |
| side effects | files created/modified by the agent |

## Key features

- **Model aliases** — map `leader` / `senior` / `junior` to concrete models in config
- **Stopwords** — break the loop on keyword match (per action)
- **Hard iteration limit** — positional arg, always enforced
- **JSONL logs** — timestamp, duration, exit code, stdout/stderr per iteration
- **Variants** — multiple outputs from one input (`--variant mk2`)
- **~200 LOC** — easy to read, audit, fork

## Configuration

Default config ships with the package. To customize:

```bash
bober init my-config.toml
```

```toml
[aliases]
leader = "composer-1.5"
senior = "composer-1.5"
junior = "composer-1"

[actions.plan]
prompt = """
1. read the file <<path>> YOU MUST NOT EDIT IT
2. plan the execution steps
3. create a self contained task description at <<outpath>>
"""

[actions.pick]
stopwords = ["BREAK-THE-LOOP"]
prompt = """
1. read the project file at <<path>>
2. pick the next task and execute it or split it
3. update the project file
4. When done put BREAK-THE-LOOP in your output
"""
```

Placeholders: `<<path>>`, `<<outpath>>`, `<<logpath>>`, `<<variant>>` — replaced at runtime.

## Limitations

- Only **Cursor CLI** (`agent`) as backend for now
- No parallel agent execution (keeps sync simple)

## Why "Bober"

[Bober kurwa](https://knowyourmeme.com/memes/bober-kurwa) — a meme-famous Polish beaver. Beavers build things.
