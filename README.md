# Bober

Lightweight agentic loop / harness. Under 200 lines of Python.

Write your program as a markdown file. Bober runs an AI agent on it in a loop — with model aliases, stopwords, iteration limits, and JSONL logs.

Inspired by [Ralph](https://github.com/karpathy/ralph) and [Autoresearch](https://github.com/lemonodor/autoresearch).

## Install

```bash
uv tool install git+https://github.com/mobarski/bober
```

## Quick start

```bash
bober plan inbox/task1.md          # plan execution, produce .out.md
bober loop inbox/task1.md 20       # run the loop (max 20 iterations)
```

With a named variant:

```bash
bober plan inbox/task1.md --variant mk2
bober loop inbox/task1.md 20 --variant mk2
```

## How it works

1. You write a task in markdown (the "program")
2. `bober plan` asks the agent to read it and produce an execution plan
3. `bober loop` runs the agent repeatedly — each iteration reads the task, does work, updates progress

The loop stops when:
- a **stopword** appears in stdout/stderr (e.g. `BREAK-THE-LOOP`)
- the agent returns a **non-zero exit code**
- the **iteration limit** is reached

## Example task

```markdown
# Task
- create empty file "hello.py"
- write hello world program in this file
- execute it with uv
- log output to "output.txt"
```

## Key features

| Feature | Details |
|---|---|
| **Model aliases** | Map `leader`, `senior`, `junior` to concrete models in config |
| **Stopwords** | Break the loop on keyword match (configurable per action) |
| **Hard iteration limit** | Passed as a positional arg |
| **JSONL logs** | Every iteration logged with timestamp, duration, exit code, stdout/stderr |
| **Unix-like I/O** | stdin (task file) → stdout/stderr (agent output) + side effects (files) |
| **Variants** | Produce multiple outputs from one input (`--variant mk2`) |
| **Tiny codebase** | ~200 LOC — easy to read, audit, and fork |

## Configuration

Bober ships with a default `bober.toml`. To customize:

```bash
bober init my-config.toml
```

Example config:

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
loop = 10
stopwords = ["BREAK-THE-LOOP"]
prompt = """
1. read the project file at <<path>>
2. pick the next task and execute it or split it
3. update the project file
5. When done put BREAK-THE-LOOP in your output
"""
```

Prompts use `<<path>>`, `<<outpath>>`, `<<logpath>>`, `<<variant>>` as placeholders.

## Limitations

- Currently uses **Cursor CLI** (`agent`) as the only backend
- No parallel agent execution (keeps synchronization simple)

## Why "Bober"

- A [meme-famous Polish beaver](https://knowyourmeme.com/memes/bober-kurwa)
- Beavers build things
