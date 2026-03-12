# Bober

Lightweight agentic loop / harness. Under 200 lines of Python — easy to read and audit.

Inspired by [ralph](https://github.com/snarktank/ralph) and [autoresearch](https://github.com/karpathy/autoresearch).

**Core idea:** your program is a markdown file. Bober feeds it to an AI agent in a loop, tracks progress, and stops when done.

## Why

- Executable specification — write *what* you want in markdown, let the agent figure out *how*
- Produce multiple variants from a single input
- Simple observability via JSONL logs

## How it works

Think of it like a unix process:

| Concept | Bober equivalent |
|---------|-----------------|
| stdin   | `path` — your program (markdown) |
| stdout  | `outpath` — execution output (markdown) |
| stderr  | `logpath` — structured logs (JSONL) |
| side effects | file changes made by the agent |

The loop runs until one of:
- a **stopword** appears in agent output (configurable per action)
- a **non-zero exit code** from the agent
- the **hard iteration limit** is reached

## Install

```
uv tool install git+https://github.com/mobarski/bober
```

Requires [Cursor CLI](https://cursor.com/cli) — install it and log in to your account.

## Quick start

```bash
# create config at ~/.config/bober/bober.toml
bober init

# plan execution for a task
bober plan inbox/task1.md

# run the loop (max 20 iterations)
bober loop inbox/task1.md 20
```

### Variants

Run different strategies on the same input:

```bash
bober plan inbox/task1.md --variant mk2
bober loop inbox/task1.md 20 --variant mk2
```

Output files are namespaced by variant: `task1.mk2.md`, `task1.mk2.jsonl`.

## Configuration

Resolved in order (first wins):

1. `--config path` CLI option
2. `BOBER_CONFIG` env variable
3. `~/.config/bober/bober.toml`
4. Bundled default config

### Config format

```toml
[defaults]
variant = 'mk1'

[aliases]
leader = "composer-1.5"
senior = "composer-1.5"
junior = "composer-1"

[actions.plan]
prompt = """
1. read the file <<path>> ...
2. plan the execution steps
3. create a self contained task at <<outpath>>
"""

[actions.pick]
loop = 10
stopwords = ["BREAK-THE-LOOP"]
prompt = """..."""
```

**Placeholders** in prompts: `<<path>>`, `<<outpath>>`, `<<logpath>>`, `<<variant>>`

**Model aliases** let you assign roles (`leader`, `senior`, `junior`) to specific models and switch them in one place.

## Limitations

- Only supports [Cursor CLI](https://cursor.com/cli) as the agent backend (for now)
- No parallel agent invocation (keeps synchronization simple)

## Name

A well-known memetic Polish animal. Beavers build things... and only sometimes cause flooding or drought ;)
