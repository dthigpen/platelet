import argparse
import os
import re
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


def exists(string: str) -> str:
    if not os.path.exists(string):
        raise ValueError(f'{string} does not exist')
    return string


def extant_dir(string: str) -> str:
    exists(string)
    if not os.path.isdir(string):
        raise ValueError(f'{string} is not a directory')
    return string


def extant_file(string: str) -> str:
    exists(string)
    if not os.path.isfile(string):
        raise ValueError(f'{string} is not a file')
    return string


def write_template(path: str, value: Union[dict, str, None], level=0, verbose=False, dryrun=False):
    '''Recursively write a file structure'''
    path = os.path.normpath(path)
    if verbose or dryrun:
        print('  ' * level + os.path.basename(path))

    if value is None:
        if not dryrun: os.makedirs(path, exist_ok=True)
    elif isinstance(value, str):
        if not dryrun:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(value)
    elif isinstance(value, dict):
        if not dryrun:
            os.makedirs(path, exist_ok=True)
        for subdir, subvalue in value.items():
            write_template(os.path.join(path, subdir), subvalue, level=level+1, verbose=verbose, dryrun=dryrun)
    else:
        raise ValueError(f'Malformed template element: {value}')


def get_args():
    '''Parse the arguments passed into the program'''
    parser = argparse.ArgumentParser(description='Create a file structure based on the given template')
    parser.add_argument('template', type=extant_file, help='YAML formatted template file')
    parser.add_argument('--path', type=extant_dir, default=get_script_path(), help='output directory')
    parser.add_argument('--vars', action='store_true', help='Print the variables used in the template, then exit')
    parser.add_argument('-v','--verbose', action='store_true', help='Print the file tree as it is written')
    parser.add_argument('-d','--dryrun', action='store_true', help='Print the file tree without changing the filesystem')
    return parser.parse_known_args()



def print_vars():
    var_names = set(re.findall(r'\$\w+', f.read()))
    if var_names:
        print('Variables:')
        print(', '.join(var_names))
    else:
        print('No variables')

if __name__ == '__main__':
    args, extras = get_args()
    variables = get_variables_from_args(extras)

    with open(args.template, 'r') as f:
        if args.vars:
            print_vars()
        else:
            contents = replace_variables(f.read(), variables)
            template = yaml.safe_load(contents)
            write_template(args.path, template, verbose=args.verbose, dryrun=args.dryrun)
