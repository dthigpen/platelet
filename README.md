# platelet
A simple program to create file structures from templates

## Usage
```
usage: platelet.py [-h] [--path PATH] [--vars] [-v] [-d] template

Create a file structure based on the given template

positional arguments:
  template       YAML formatted template file

optional arguments:
  -h, --help     show this help message and exit
  --path PATH    output directory
  --vars         Print the variables used in the template, then exit
  -v, --verbose  Print the file tree as it is written
  -d, --dryrun   Print the file tree without changing the filesystem

```
## Example
Create a template file for your file structure. For example `template.yaml`
```yaml
dir1:
    config: |
        file contents
        be sure to use the | or |-
dir2/empty_dir:
dir4/dir5/file1.json: ''
```
Run the program in the directory you want to create the file structure.
```
py platelet.py template.yaml
```
Optionally specify a path to create it in a different directory.
```
py platelet.py template.yaml --path ~/some/dir
```
Make variable replacements by including `$<varname>` in your template file.
```
$proj/
    src/$proj.java
```
```
py platelet.py template.yaml proj=my_thing
```