import subprocess
import os
import sys
from time import time
from datetime import datetime
import tomllib
from types import SimpleNamespace
import json
from importlib.resources import files
from pathlib import Path

try:
    from rich import print
except ImportError:
    pass

CONFIG_BUNDLED_PATH = files(__package__).joinpath('bober.toml')
CONFIG_USER_PATH = Path.home() / '.config' / 'bober' / 'bober.toml'
HELP_TEXT = """
Usage: bober <action> <path> [loop=1] [options]

Actions:
    help      show this help
    init      initialize a new config file at <path>
    plan      plan the execution for program at <path>
    pick      pick the next task for program at <path>

Options:
    --model <model>     use a specific model
    --mode <mode>       use a specific mode
    --variant <variant> use a specific variant
    --work <dir>        output directory (default: dirname of path)
"""
state = SimpleNamespace()
state.config = {}

### API SURFACE ###############################################################################

def do_loop(action: str, path: str, /, loop=1, mode=None, model=None, stopwords=None, variant=None, work=None):
    assert loop > 0, 'loop must be positive'
    variant = variant or _get_default_variant()
    work = _get_default_work(path, work)
    outpath = _get_default_outpath(action, path, variant=variant, work=work)
    logpath = _get_default_logpath(action, path, variant=variant, work=work)
    stopwords = stopwords or _get_stopwords(action)
    model = model or _get_model(action)
    model = _resolve_model(model)
    for i in range(1,loop+1):
        result = _do_task(action, path, outpath=outpath, logpath=logpath, work=work, mode=mode, model=model, variant=variant, step=i, nsteps=loop)
        if logpath:
            with open(logpath, 'a') as f:
                f.write(json.dumps(result) + '\n')
        if result['returncode'] != 0:
            result['stop'] = 'returncode'
            break
        if any(word in result['stdout'] for word in stopwords):
            result['stop'] = 'stopwords.stdout'
            break
        if any(word in result['stderr'] for word in stopwords):
            result['stop'] = 'stopwords.stderr'
            break
        print(result) # TODO: add stop reason
    else:
        result['stop'] = 'max_iterations'
        return
    print(result)


def load_config(cli_config=None):
    path = _resolve_config_path(cli_config)
    with open(path, 'rb') as f:
        state.config = tomllib.load(f)


def init_config(path=None):
    path = path or CONFIG_USER_PATH
    if Path(path).exists():
        raise ValueError(f'Config file {path} already exists')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(open(CONFIG_BUNDLED_PATH, 'r').read())


### INTERNALS #################################################################################

def _do_task(action:str, path: str, /, outpath=None, logpath=None, work=None, mode=None, model=None, variant=None, step=1, nsteps=1):
    t0 = time()
    variant = variant or ''
    if not os.path.exists(path):
        returncode = 129 # ENOENT: No such file or directory
        stdout = ''
        stderr = f'File {path} not found'
    else:
        prompt = _get_prompt(action)
        prompt = prompt.replace('<<path>>', path)
        prompt = prompt.replace('<<stem>>', Path(path).stem)
        prompt = prompt.replace('<<work>>', work or '')
        prompt = prompt.replace('<<variant>>', variant)
        prompt = prompt.replace('<<outpath>>', outpath)
        prompt = prompt.replace('<<logpath>>', logpath)
        prompt = prompt.replace('<<step>>', str(step))
        prompt = prompt.replace('<<nsteps>>', str(nsteps))
        #
        cmd = _agent_cmd(prompt, mode=mode, model=model)
        imode = os.stat(path).st_mode # original permissions
        os.chmod(path, 0o400) # read-only for the agent
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True)
        finally:
            os.chmod(path, imode) # restore original permissions
        #
        returncode = result.returncode
        stdout = result.stdout.decode()
        stderr = result.stderr.decode()
    return {
        'ts': datetime.fromtimestamp(t0).isoformat(),
        'action': action,
        'path': path,
        'variant': variant,
        'returncode': returncode,
        'time': time() - t0,
        'mode': mode,
        'model': model,
        'stdout': stdout,
        'stderr': stderr,
        'step': step,
        'nsteps': nsteps,
    }

def _agent_cmd(prompt: str, mode=None, model=None):
    cmd = f'''agent --trust --yolo -p "{prompt}"'''
    if mode:
        cmd += f' --mode {mode}'
    if model:
        cmd += f' --model {model}'
    return cmd


def _resolve_model(model=None):
    model = model or 'leader'
    model = state.config.get('aliases', {}).get(model, model) or 'auto'
    return model


def _get_model(action: str):
    return state.config.get('actions', {}).get(action, {}).get('model')


def _get_prompt(action: str):
    return state.config.get('actions', {}).get(action, {})['prompt']


def _get_stopwords(action: str):
    return state.config.get('actions', {}).get(action, {}).get('stopwords', [])


def _get_default_work(path: str, work=None):
    if work:
        return work.rstrip('/')
    return str(Path(path).parent)


def _get_default_outpath(action: str, path: str, variant=None, work=None):
    stem = Path(path).stem
    work = _get_default_work(path, work)
    if variant:
        return f'{work}/{stem}.{variant}.out.md'
    else:
        return f'{work}/{stem}.out.md'


def _get_default_logpath(action: str, path: str, variant=None, work=None):
    stem = Path(path).stem
    work = _get_default_work(path, work)
    if variant:
        return f'{work}/{stem}.{variant}.log.jsonl'
    else:
        return f'{work}/{stem}.log.jsonl'


def _get_default_variant():
    return state.config.get('defaults', {}).get('variant', '')


def _resolve_config_path(cli_config=None):
    if cli_config:
        return cli_config
    env = os.environ.get('BOBER_CONFIG')
    if env:
        return env
    user = CONFIG_USER_PATH
    if user.exists():
        return user
    return CONFIG_BUNDLED_PATH


### CLI #########################################################################################

def _show_help():
    print(HELP_TEXT)


def main_cli():
    # kind of ugly... but small, simple and works
    args = sys.argv[1:]
    if not args:
        return _show_help()
    action = args.pop(0)
    kwargs = {}
    if not args:
        if action == 'init':
            init_config()
            return
        return _show_help()
    path = args.pop(0)
    if args and args[0].isdigit():
        kwargs['loop'] = int(args.pop(0))
    if len(args) % 2 != 0:
        return _show_help()
    while args:
        key = args.pop(0)
        if not key.startswith('--'):
            return _show_help()
        key = key.lstrip('--')
        if key not in ['model', 'mode', 'variant', 'config', 'work']:
            return _show_help()
        value = args.pop(0)
        kwargs[key] = value
    if action == 'init':
        init_config(path)
        return
    config = kwargs.pop('config', None)
    load_config(config)
    actions = state.config.get('actions', {}).keys()
    if action not in ['help', 'init'] + list(actions):
        return _show_help()
    do_loop(action, path, **kwargs)


if __name__ == '__main__':
    main_cli()

# TODO: model switching from prompt
