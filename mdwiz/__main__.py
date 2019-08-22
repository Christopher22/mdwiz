import sys
from pathlib import Path
from typing import Optional
from enum import Enum
import logging

import pyperclip

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


class MdwizRuntimeError(Exception):
    def __init__(code: StatusCode):
        assert code != StatusCode.Success, "Could not throw error on success"
        super().__init__(code.name)
        self.status_code = code.value


def get_file(file_type: FileType, required: bool = False, **kwargs) -> Optional[Path]:
    # Find all the files of interest
    files = file_type.locate_files(Path.cwd(), **kwargs)

    if len(files) == 0:
        # Fail if a required filetype is not found, otherwise print an warning
        if required:
            logging.error(file_type.missing_file_error_msg())
            raise MdwizRuntimeError(StatusCode.FileError)
        else:
            logging.info(f"{file_type.__class__.__name__} is skipped.")
        return None
    elif len(files) == 1:
        logging.info(f"Using '{files[0]}' as {file_type.__class__.__name__} file.")
        return files[0]
    else:
        # Fail if multiple files are possible
        logging.error(file_type.multiple_files_error_msg())
        raise MdwizRuntimeError(StatusCode.FileError)


def main() -> StatusCode:
    # Configure the general output format
    logging.basicConfig(
        stream=sys.stderr, format="[%(levelname)s]\t%(message)s", level=logging.DEBUG
    )

    # Check dependencies
    if not Converter.is_available():
        logging.error("Pandoc is not installed. Please install to proceed.")
        return StatusCode.MissingDependency
    elif not Bibliography.is_available():
        logging.error("Pandoc-citeproc is not installed. Please install to proceed.")
        return StatusCode.MissingDependency

    try:
        # Load the files of interest and create a Converter object with them
        markdown_file = get_file(Markdown(), required=True, recursive=False)
        converter = Converter(
            markdown_file,
            citation_file=get_file(
                BibliographyFileType(), reference_file=markdown_file
            ),
            template_file=get_file(Template(), reference_file=markdown_file),
        )
    except MdwizRuntimeError as runtime_error:
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
    sys.exit(main().value)
