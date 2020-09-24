import argparse
import logging
import os
import sys
import warnings
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Sequence

import pyperclip

from mdwiz import NAME, DESCRIPTION
from mdwiz.bibliography import Bibliography
from mdwiz.converter import Converter
from mdwiz.filetypes import FileType
from mdwiz.filetypes.bibliography import Bibliography as BibliographyFileType
from mdwiz.filetypes.csl import Csl
from mdwiz.filetypes.markdown import Markdown
from mdwiz.filetypes.template import Template


class StatusCode(Enum):
    Success = 0
    FileError = 1
    PandocError = 2
    MissingDependency = 3

    def __int__(self):
        return self.value

    def is_successfull(self) -> bool:
        return self == StatusCode.Success


class MdwizRuntimeError(Exception):
    def __init__(self, code: StatusCode, msg: str):
        assert code != StatusCode.Success, "Could not throw error on success"
        super().__init__(msg)
        self.msg = msg
        self.status_code = code

    def log(self):
        logging.error(self.msg)


def get_file(
        file_type: FileType,
        given_file: Optional[str] = None,
        required: bool = False,
        multiple_files: bool = False,
        **kwargs,
) -> Optional[Union[Path, Sequence[Path]]]:
    # Check if the user has provided an file
    if given_file is not None and len(given_file) > 0:
        given_file = Path.cwd() / given_file
        if not given_file.is_file():
            raise MdwizRuntimeError(
                StatusCode.FileError, f"Provided file '{given_file}' not found!"
            )
        logging.info(f"Using '{given_file}' as {file_type.__class__.__name__} file.")
        return given_file

    # Find all the files of interest which are bigger than 5 bytes
    files = file_type.locate_files(Path.cwd(), min_size=5, **kwargs)

    if len(files) == 0:
        # Fail if a required filetype is not found, otherwise print an warning
        if required:
            raise MdwizRuntimeError(
                StatusCode.FileError, file_type.missing_file_error_msg()
            )
        else:
            logging.info(f"{file_type.__class__.__name__} is skipped.")
        return None
    elif len(files) == 1:
        logging.info(f"Using '{files[0]}' as {file_type.__class__.__name__} file.")
        return files[0] if not multiple_files else files
    else:
        if not multiple_files:
            # Fail if multiple files are possible
            raise MdwizRuntimeError(
                StatusCode.FileError, file_type.multiple_files_error_msg()
            )
        return files


def main() -> StatusCode:
    # Configure the general output format and warnings
    logging.basicConfig(
        stream=sys.stderr, format="[%(levelname)s] %(message)s", level=logging.DEBUG
    )
    logging.captureWarnings(True)
    warnings.formatwarning = lambda message, category, filename, lineno, line: message

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog=NAME, description=DESCRIPTION, add_help=True, allow_abbrev=True
    )
    parser.add_argument(
        "--markdown",
        help="The markdown file which should be converted. If not specified, it is determined automatically.",
        type=str,
    )
    parser.add_argument(
        "--template",
        help="An optional template for the output. If not specified, it is determined automatically.",
        type=str,
    )
    parser.add_argument(
        "--bibliography",
        help="An optional bibliography for the output. If not specified, it is determined automatically.",
        type=str,
    )
    parser.add_argument(
        "--output",
        help="An explicit output file to write. Useful on Microsoft Windows, because the console might otherwise fail on UTF-8 data.",
        type=str,
        default="",
    )
    parser.add_argument(
        "--csl",
        help="A definition file for the Citation Style Language.",
        type=str,
        default="",
    )

    arguments = parser.parse_args()

    # Check dependencies
    if not Converter.is_available():
        logging.error("Pandoc is not installed. Please install to proceed.")
        return StatusCode.MissingDependency
    elif not Bibliography.is_available():
        logging.error("Pandoc-citeproc is not installed. Please install to proceed.")
        return StatusCode.MissingDependency

    try:
        # Load the files of interest and create a Converter object with them
        markdown_file = get_file(
            Markdown(),
            given_file=arguments.markdown,
            required=True,
            recursive=False,
            multiple_files=True,
        )
        converter = Converter(
            markdown_file,
            citation_file=get_file(
                BibliographyFileType(),
                given_file=arguments.bibliography,
                reference_file=markdown_file,
            ),
            template_file=get_file(
                Template(), given_file=arguments.template, reference_file=markdown_file
            ),
            csl_file=get_file(
                Csl(), given_file=arguments.csl, reference_file=markdown_file
            ),
        )
    except MdwizRuntimeError as runtime_error:
        runtime_error.log()
        return runtime_error.status_code

    # Convert the file
    try:
        converted_file = converter.convert()
    except Exception as ex:
        logging.error(str(ex))
        return StatusCode.PandocError

    # Copy the converted file to the clipboard if called correctly or write it into the command line pipeline.
    if len(arguments.output) > 0:
        with Path(arguments.output).open("w", encoding="utf-8") as file:
            file.write(converted_file)
    elif sys.stdout.isatty():
        pyperclip.copy(converted_file)
    else:
        try:
            print(converted_file)
        except UnicodeEncodeError:
            # Some hacks for Windows to fix the bugs regarding IO
            if os.name == "nt":
                logging.warning(
                    "Unable to output due to Windows console issue, use --output as bugfix. No output written."
                )

    return StatusCode.Success


if __name__ == "__main__":
    result = main()
    if result is not StatusCode.Success:
        sys.exit(result.value)
