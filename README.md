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
| stdout  | `outpath` — execution output (.out.md) |
| stderr  | `logpath` — structured logs (.log.jsonl) |
| workdir | `work` — output directory |
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

Output files are namespaced by variant: `<<outpath>>` = `inbox/task1.mk2.out.md`, `<<logpath>>` = `inbox/task1.mk2.log.jsonl`.

### Custom output directory

By default, output files land next to the input. Use `--work` to redirect:

```bash
bober plan inbox/task1.md --work output/task1
```

Now `<<work>>` = `output/task1`, `<<outpath>>` = `output/task1/task1.mk1.out.md`.

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
4. logs at <<logpath>>
"""

[actions.pick]
loop = 10
stopwords = ["BREAK-THE-LOOP"]
prompt = """..."""
```

### Placeholders

| Placeholder | Example value | Note |
|-------------|---------------|------|
| `<<path>>` | `inbox/task1.md` | full input path with extension |
| `<<stem>>` | `task1` | input filename without extension or path |
| `<<work>>` | `inbox` | output directory, no trailing `/` |
| `<<outpath>>` | `inbox/task1.mk1.out.md` | full output path |
| `<<logpath>>` | `inbox/task1.mk1.log.jsonl` | full log path |
| `<<variant>>` | `mk1` | |
| `<<step>>` | `1` | current iteration |
| `<<nsteps>>` | `10` | total iterations |

Use `<<stem>>` to compose custom paths: `<<work>>/<<stem>>.<<variant>>.<<step>>.md`

**Model aliases** let you assign roles (`leader`, `senior`, `junior`) to specific models and switch them in one place.

## Safety

The input file is made read-only (`chmod 400`) during agent execution. Not real security — just a foot-gun guard that costs nothing and saves you from the most obvious "oops".

## Logs

Each JSONL line contains: `ts`, `action`, `path`, `variant`, `step`, `nsteps`, `model`, `mode`, `returncode`, `time`, `stdout`, `stderr`, `stop`.

```bash
# failed steps
jq 'select(.returncode != 0)' task1.mk1.log.jsonl

# step times
jq '{step, time}' task1.mk1.log.jsonl
```

## Limitations

- Only supports [Cursor CLI](https://cursor.com/cli) as the agent backend (for now)
- No parallel agent invocation (keeps synchronization simple)

## Name

A well-known memetic Polish animal. Beavers build things... and only sometimes cause flooding or drought ;)
