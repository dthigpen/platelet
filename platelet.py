#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import re
import sys
from typing import Union
import yaml
from collections import OrderedDict


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
        if len(split) > 1 and len(split[0]) > 0:
            variables[split[0]] = split[1]
        else:
            raise ValueError(f'Invalid assignment: "{arg}" must take form var=value')
    return variables


def extant_file(string: str) -> Path:
    path = Path(string)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f'{string} does not exist or is not a file')
    return path


def write_template(output_path: Path, value: Union[dict, str, None], level=0, verbose=False, dryrun=False):
    '''Recursively write a file structure'''
    
    if verbose or dryrun:
        print('  ' * level + output_path.name)

    if value is None:
        if not dryrun: os.makedirs(output_path, exist_ok=True)
    elif isinstance(value, str):
        if not dryrun:
            os.makedirs(output_path.parent, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(value)
    elif isinstance(value, dict):
        if not dryrun:
            os.makedirs(output_path, exist_ok=True)
        for subdir, subvalue in value.items():
            write_template(output_path / subdir, subvalue, level=level+1, verbose=verbose, dryrun=dryrun)
    else:
        raise ValueError(f'Malformed template element: {value}')

def get_vars_from_template(content: str) -> OrderedDict:
    var_names = []
    for name in re.findall(r'\$\w+', content):
        if name[1:] not in var_names:
            var_names.append(name[1:])
    return OrderedDict.fromkeys(var_names, None)


def interactive_set_vars(variables: OrderedDict):
    for var_name in variables:
        variables[var_name] = input(f'{var_name}=')

def print_vars(content: str):
    variables = get_vars_from_template(content)
    if variables:
        print('Variables:')
        print(', '.join(variables.keys()))
    else:
        print('No variables')

def read_to_template(template_file, path, indent=0):
    indent_str = '  ' * indent
    if path.is_dir():
        template_file.write(f'{indent_str}{path.name}:\n')
        for child in path.iterdir():
            read_to_template(template_file, child, indent=indent+1)
    elif path.is_file():
        template_file.write(f'{indent_str}{path.name}: |-\n')
        with open(path, 'r') as f:
            for line in f:
                template_file.write(f'  {indent_str}{line}')
            template_file.write('\n')

def yes_no(prompt=''):
    res = input(prompt + ' (y/yes/n/no) ').lower()
    return res in ['y', 'yes']

def run(template: Path, in_or_out_path: Path, user_variables: dict, is_input_dir: bool, print_vars: bool, dry_run: bool, verbose: bool):
    if is_input_dir:
        if template.exists() and not yes_no(f'Overwrite template at {template}?'):
            print('Aborting..')
            exit(0)
                
        with open(template, 'w') as template_file:
            read_to_template(template_file, in_or_out_path)
    else:
        with open(template, 'r') as f:
            if not yes_no(f'Overwrite directories and files specified in template {template} at {in_or_out_path}'):
                print('Aborting')
                exit(0)

            file_content = f.read()
            variables = get_vars_from_template(file_content)

            # Overwrite values with user values
            for var_name in variables:
                if var_name in user_variables:
                    variables[var_name] = user_variables[var_name]

            missing_var_values = None in variables.values()
            if missing_var_values:
                print('Enter values for the following variables:')
                interactive_set_vars(variables)

            if print_vars:
                print_vars(file_content)
            else:
                contents = replace_variables(file_content, variables)
                template = yaml.safe_load(contents)
                write_template(in_or_out_path, template, verbose=verbose, dryrun=dry_run)


def get_args():
    '''Parse the arguments passed into the program'''
    parser = argparse.ArgumentParser(description='Create a file structure based on the given template')
    parser.add_argument('template', type=Path, help='YAML formatted template file')
    parser.add_argument('path', type=Path, default=os.getcwd(), help='output or input directory/file')
    parser.add_argument('--read', action='store_true', help='Read the given path to the specified template file')
    parser.add_argument('--vars', action='store_true', help='Print the variables used in the template, then exit')
    parser.add_argument('-v','--verbose', action='store_true', help='Print the file tree as it is written')
    parser.add_argument('-d','--dryrun', action='store_true', help='Print the file tree without changing the filesystem')
    return parser.parse_known_args()

if __name__ == '__main__':
    args, extras = get_args()
    user_variables = get_variables_from_args(extras)
    run(args.template, args.path, user_variables, args.read, args.vars, args.dryrun, args.verbose)

    
