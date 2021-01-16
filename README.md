# mdwiz
## THIS PROJECT IS DEPRECATED: USE THE MORE FLEXIBLE [panwiz](https://github.com/Christopher22/panwiz) INSTEAD.
**mdwiz** is a Python-based application for creating complex and scientific documents in Markdown, supporting advanced options like bibliographies and templates. It is designed as a smart wrapper around the amazing [pandoc](https://pandoc.org/), combining its powerfulness with a bunch of useful defaults and simplified use. It is primarily intended to help students in their writing of reports and theses by emphasizing a strict separation of content and presentation.

## Usage
First of all, please install this package using Python's [pip](https://pypi.org/project/pip/). If *pandoc* is not already present, it may be installed in the background: `pip install git+https://github.com/Christopher22/mdwiz`

The program can be used by open a terminal and typing in `mdwiz`. By default, this software will search for a suitable Markdown file in the provided directory. If multiple Markdown files are available or they are present in another folder, please specify the file of interest using the "--markdown" argument. For a complete list of available options, please refer to the output of `mdwiz --help`. Afterward, corresponding bibliographies and templates are recursively searched in the folder by their file ending. If multiple files are found and one has the exact stem (the part before the extension) as the  Markdown file, it is automatically chosen. An explicit file selection is possible like in the case of the Markdown file. If the output of the application is not directly written to a file, i.e. by  `mdwiz > ../output.tex`, it is copied to the clipboard to be pasted i.e. at [Overleaf](https://www.overleaf.com). Below, you find exemplary project structures on the file system.

#### Example 1: Project structure without explicit template
- README.md
- thesis
	- bibliography.bib

#### Example 2: Project structure with multiple documents
- lecture1.md <– You would need to specify one of these Markdown explicitly, but afterward everything is handled automatically
- lecture2.md
- bibliographies
	- lecture1.bib
	- lecture2.bib
- design
	- template.tex 

