import subprocess
import os
import sys
from time import time
from datetime import datetime
import tomllib
from types import SimpleNamespace
import json
from importlib.resources import files

try:
    from rich import print
except ImportError:
    pass

CONFIG_PATH = files(__package__).joinpath('bober.toml')

state = SimpleNamespace()
state.config = {}

### API SURFACE ###############################################################################

def do_loop(action: str, path: str, /, loop=1, mode=None, model=None, stopwords=None):
    assert loop > 0, 'loop must be positive'
    outpath = _get_default_outpath(action, path)
    logpath = _get_default_logpath(action, path)
    stopwords = stopwords or _get_stopwords(action)
    model = model or _get_model(action)
    model = _resolve_model(model)
    for i in range(1,loop+1):
        result = _do_task(action, path, outpath=outpath, logpath=logpath, mode=mode, model=model)
        result['iteration'] = i
        result['max_iterations'] = loop
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


def load_config(path=None):
    if state.config and not path:
        return  # do not load the default config if some config is already loaded
    with open(path or CONFIG_PATH, 'rb') as f:
        state.config = tomllib.load(f)


def init_config(path):
    if os.path.exists(path):
        raise ValueError(f'Config file {path} already exists')
    default_config = "TODO" # TODO: read from package assets
    with open(path, 'w') as f:
        f.write(default_config)


### INTERNALS #################################################################################

def _do_task(action:str, path: str, /, outpath=None, logpath=None, mode=None, model=None):
    t0 = time()
    if not os.path.exists(path):
        returncode = 129 # ENOENT: No such file or directory
        stdout = ''
        stderr = f'File {path} not found'
    else:
        prompt = _get_prompt(action)
        prompt = prompt.replace('<<path>>', path)
        prompt = prompt.replace('<<outpath>>', outpath)
        prompt = prompt.replace('<<logpath>>', logpath)
        #
        cmd = _agent_cmd(prompt, mode=mode, model=model)
        result = subprocess.run(cmd, shell=True, capture_output=True)
        returncode = result.returncode
        stdout = result.stdout.decode()
        stderr = result.stderr.decode()
    return {
        'ts': datetime.fromtimestamp(t0).isoformat(),
        'action': action,
        'path': path,
        'returncode': returncode,
        'time': time() - t0,
        'mode': mode,
        'model': model,
        'stdout': stdout,
        'stderr': stderr,
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


def _get_default_outpath(action: str, path: str):
    return path + '.out.md' # TODO


def _get_default_logpath(action: str, path: str):
    return path + '.log.jsonl' # TODO


def show_help():
    print("TODO: show help")


def main_cli():
    # kind of ugly... but small, simple and works
    args = sys.argv[1:]
    if not args:
        return show_help()
    action = args.pop(0)
    load_config()
    kwargs = {}
    actions = state.config.get('actions', {}).keys()
    if action not in ['help', 'init'] + list(actions):
        return show_help()
    if not args:
        return show_help()
    path = args.pop(0)
    if args and args[0].isdigit():
        kwargs['loop'] = int(args.pop(0))
    if len(args) % 2 != 0:
        return show_help()
    while args:
        key = args.pop(0)
        if not key.startswith('--'):
            return show_help()
        key = key.lstrip('--')
        if key not in ['model', 'mode']:
            return show_help()
        value = args.pop(0)
        kwargs[key] = value
    do_loop(action, path, **kwargs)


if __name__ == '__main__':
    if False:
        load_config()
        do_loop('plan', 'tests/assets/task1.md')
        do_loop('pick', 'tests/assets/task1.md', loop=10)
    else:
        main_cli()

# TODO: model switching from prompt
# TODO: jump back
