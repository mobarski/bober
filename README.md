# Bober

Lightweight agentic loop / harness. Under 200 lines of Python — easy to read, audit, and extend.

Inspired by [ralph](https://github.com/snarktank/ralph) and [autoresearch](https://github.com/karpathy/autoresearch).

**Core idea:** write an executable specification in Markdown, let an agent run it in a loop.

## Features

- **Model aliases** — map `leader` / `senior` / `junior` to concrete models, pick the right size for the job
- **Loop stopwords** — agent can break the loop by emitting a keyword (e.g. `BREAK-THE-LOOP`)
- **Hard iteration limit** — always bounded, no runaway loops
- **Config-driven** — prompts and settings live in a TOML file, CLI stays minimal
- **JSONL logs** — every iteration logged for observability and post-mortem
- **Unix process analogy:**
  - stdin → `path` (your Markdown program)
  - stdout → `outpath` (execution output, also Markdown)
  - stderr → `logpath` (JSONL agent logs)
  - side effects → file changes on disk
- **Variants** — produce multiple outputs from a single input

## Install

```bash
uv tool install git+https://github.com/mobarski/bober
```

## Quick start

Plan the execution, then run it:

```bash
bober plan inbox/task1.md
bober loop inbox/task1.md 20
```

With a named variant:

```bash
bober plan inbox/task1.md --variant mk2
bober loop inbox/task1.md 20 --variant mk2
```

## Usage

```
bober <action> <path> [loop] [options]

Actions:
    help      show help
    init      create a new config file at <path>
    plan      plan execution for the program at <path>
    pick      pick the next task from the program at <path>

Options:
    --model <model>       model name or alias
    --mode <mode>         agent mode
    --variant <variant>   output variant name
```

## Configuration

Default config is bundled (`bober.toml`). Create your own with:

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
stopwords = ["BREAK-THE-LOOP"]
prompt = """
1. read the project file at <<path>>
2. pick the next task and execute it or split it
3. update the project file
4. When everything is done put BREAK-THE-LOOP keyword in your output
"""
```

Placeholders in prompts: `<<path>>`, `<<outpath>>`, `<<logpath>>`, `<<variant>>`.

## Limitations

- Agent backend: Cursor CLI only (for now)
- No parallel agent execution (keeps synchronization simple)

## Why "Bober"

Beavers build things... and only sometimes cause floods.
