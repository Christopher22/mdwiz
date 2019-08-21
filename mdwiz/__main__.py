import sys
from pathlib import Path
from typing import Type, Optional
from enum import Enum
import logging

import pyperclip

from mdwiz.converter import Converter
from mdwiz.filetypes.markdown import Markdown
from mdwiz.filetypes.bibliography import Bibliography
from mdwiz.filetypes.template import Template


class ErrorCode(Enum):
    FileError = 1
    PandocError = 2


def get_file(file_type: Type, required: bool = False, **kwargs) -> Optional[Path]:
    # Find all the files of interest
    file_type = (file_type)()
    files = file_type.locate_files(Path.cwd(), **kwargs)

    if len(files) == 0:
        # Fail if a required filetype is not found, otherwise print an warning
        if required:
            logging.error(file_type.missing_file_error_msg())
            sys.exit(ErrorCode.FileError)
        else:
            logging.info(f"{file_type.__class__.__name__} is skipped.")
        return None
    elif len(files) == 1:
        logging.info(f"Using '{files[0]}' as {file_type.__class__.__name__} file.")
        return files[0]
    else:
        # Fail if multiple files are possible
        logging.error(file_type.multiple_files_error_msg())
        sys.exit(ErrorCode.FileError)


def main():
    # Configure the general output format
    logging.basicConfig(
        stream=sys.stderr, format="[%(levelname)s]\t%(message)s", level=logging.DEBUG
    )

    # Load the files of interest and create a Converter object with them
    markdown_file = get_file(Markdown, required=True, recursive=False)
    converter = Converter(
        markdown_file,
        citation_file=get_file(Bibliography, reference_file=markdown_file),
        template_file=get_file(Template, reference_file=markdown_file),
    )

    # Convert the file
    try:
        converted_file = converter.convert()
    except Exception as ex:
        logging.error(str(ex))
        sys.exit(ErrorCode.PandocError)

    # Copy the converted file to the clipboard if called correctly or write it into the command line pipeline.
    if sys.stdout.isatty():
        pyperclip.copy(converted_file)
    else:
        print(converted_file)


if __name__ == "__main__":
    main()
