import sys
from pathlib import Path
from typing import Optional
from enum import Enum
import logging
import argparse

import pyperclip

from mdwiz import NAME, DESCRIPTION
from mdwiz.converter import Converter
from mdwiz.bibliography import Bibliography
from mdwiz.filetypes import FileType
from mdwiz.filetypes.markdown import Markdown
from mdwiz.filetypes.bibliography import Bibliography as BibliographyFileType
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
    def __init__(code: StatusCode, msg: str):
        assert code != StatusCode.Success, "Could not throw error on success"
        super().__init__(msg)
        self.msg = msg
        self.status_code = code.value

    def log(self):
        logging.error(self.msg)


def get_file(
    file_type: FileType,
    given_file: Optional[str] = None,
    required: bool = False,
    **kwargs,
) -> Optional[Path]:
    # Check if the user has provided an file
    if given_file is not None:
        given_file = Path.cwd() / given_file
        if not given_file.is_file():
            raise MdwizRuntimeError(
                StatusCode.FileError, f"Provided file '{given_file}' not found!"
            )
        logging.info(f"Using '{given_file}' as {file_type.__class__.__name__} file.")
        return given_file

    # Find all the files of interest
    files = file_type.locate_files(Path.cwd(), **kwargs)

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
        return files[0]
    else:
        # Fail if multiple files are possible
        raise MdwizRuntimeError(
            StatusCode.FileError, file_type.multiple_files_error_msg()
        )


def main() -> StatusCode:
    # Configure the general output format
    logging.basicConfig(
        stream=sys.stderr, format="[%(levelname)s]\t%(message)s", level=logging.DEBUG
    )

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
            Markdown(), given_file=arguments.markdown, required=True, recursive=False
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
    if sys.stdout.isatty():
        pyperclip.copy(converted_file)
    else:
        print(converted_file)


if __name__ == "__main__":
    sys.exit(int(main()))
