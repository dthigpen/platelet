import argparse
import os
import sys
from typing import Union
import yaml


def replace_variables(content: str, variables: dict) -> str:
    '''Replace all variables with their values'''
    for var, value in variables.items():
        content = content.replace('$' + var, value)
    return content


def get_variables_from_args(args: str) -> dict:
    '''Turn the extra arguments into variables'''
    variables = {}
    for arg in args:
        split = arg.split('=', 1)
        if len(split) > 0 and len(split[0]) > 0:
            variables[split[0]] = split[1]
    return variables


def get_script_path() -> str:
    '''Get the execution directory of the script'''
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def validate_args(args: argparse.Namespace) -> None:
    '''Checks that the command line arguments are valid'''
    if not os.path.exists(args.template):
        raise Exception(f'Given template {args.template} does not exist')
    if not os.path.isfile(args.template):
        raise Exception(f'Given template {args.template} is not a file')
    if not os.path.exists(args.path):
        raise Exception(f'Given path {args.path} does not exist')
    if not os.path.isdir(args.path):
        raise Exception(f'Given path {args.path} is not a directory')

def get_args():
    parser = argparse.ArgumentParser(description='Create a file structure based on the given template')
    parser.add_argument('template')
    parser.add_argument('--path', default=get_script_path())
    return parser.parse_known_args()


def write_template(path: str, value: Union[dict, str, None], level=0):
    '''Recursively write a file structure'''
    path = os.path.normpath(path)
    print('  ' * level + os.path.basename(path))
    if value is None:
        os.makedirs(path, exist_ok=True)
    elif isinstance(value, str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(value)
    elif isinstance(value, dict):
        os.makedirs(path, exist_ok=True)
        for subdir, subvalue in value.items():
            write_template(os.path.join(path, subdir), subvalue, level=level+1)
    else:
        raise ValueError(f'Malformed template element: {value}')

if __name__ == '__main__':
    args, extras = get_args()
    variables = get_variables_from_args(extras)

    with open(args.template, 'r') as f:
        contents = replace_variables(f.read(), variables)
        template = yaml.safe_load(contents)
        write_template(args.path, template)
