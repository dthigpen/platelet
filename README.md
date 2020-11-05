# platelet
A simple program to create file structures from templates

## Usage
Create a template file for your file structure. For example `template.txt`
```
dir1/
    .config
        foo=bar
dir2/dir3/
dir4/dir5/file1.json
```
Run the program in the directory you want to create the file structure.
```
py platelet.py template.txt
```
Optionally specify a path to create it in a different directory.
```
py platelet.py template.txt --path ~/some/dir
```
Make variable replacements by including `$<varname>` in your template file.
```
$proj/
    src/$proj.java
```
```
py platelet.py template.txt proj=my_thing
```