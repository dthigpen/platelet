import argparse
import os
import sys
import re

INDENT = '    '

def get_indent(line: str) -> int:
    '''Get the number of indentations the line has'''
    p = re.compile('^ *')
    return len(p.match(line).group(0)) / len(INDENT)


def is_file(name: str) -> bool:
    return name[-1:] != "/"


def is_dir(name: str) -> bool:
    return name[-1:] == "/"


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

        
def create(dir: str, lines: list) -> None:
    '''Build a the file structure provided by the given lines'''
    stack = []
    last_indent = 0
    line_num = 0
    while len(lines) > 0:
        line = lines.pop(0)
        line_num += 1
        p = re.compile(r'^\s*')
        match = p.match(line)
        line = match.group(0).replace('\t',INDENT) + line[match.end(0):]
        indent = get_indent(line)
        trimmed = line.strip()
        
        # pop number of dirs equivalent to difference in indents
        if indent < last_indent:
            for i in range(int(last_indent - indent)):
                dir = os.path.dirname(dir)
        elif indent != last_indent:
            raise Exception(f'Unexpected indentation on line {line_num}: {line}')


        if is_dir(trimmed):
            # print('create dir:', trimmed)
            dir = os.path.join(dir, trimmed)
            if not os.path.exists(dir):
                os.makedirs(dir)
            indent += 1
        elif is_file(trimmed):
            # print('create file:', trimmed)
            with open(os.path.join(dir,trimmed), 'w') as f:
                    while len(lines) > 0:
                        line = lines[0]
                        if get_indent(line) >= indent + 1:
                            lines.pop(0)
                            line_num += 1
                            line = line[int((indent + 1) * len(INDENT)):]
                            f.write(line + '\n')
                        else:
                            break
        else:
            raise Exception(f'Bad token on line {line_num}: {line}')
        last_indent = indent

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a file structure based on the given template')
    parser.add_argument('template')
    parser.add_argument('--path', default=get_script_path())
    args, extras = parser.parse_known_args()

    try:
        validate_args(args)
        variables = get_variables_from_args(extras)
        template_contents = open(args.template, 'r').read()
        template_contents = replace_variables(template_contents, variables)
        lines = template_contents.split('\n')
        create(args.path, lines)
    except Exception  as e:
        print(e)
        exit(1)