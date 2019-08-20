import sys
from pathlib import Path
from typing import Type, Optional
import logging

import pyperclip

from mdwiz.converter import Converter
from mdwiz.filetypes.markdown import Markdown
from mdwiz.filetypes.bibliography import Bibliography
from mdwiz.filetypes.template import Template


def get_file(file_type: Type, required: bool = False, **kwargs) -> Optional[Path]:
    file_type = (file_type)()
    files = file_type.locate_files(Path.cwd(), **kwargs)

    if len(files) == 0:
        if required:
            logging.error(file_type.missing_file_error_msg())
            exit()
        else:
            logging.info(f"{file_type.__class__.__name__} is skipped.")
            
        return None
    elif len(files) == 1:
        return files[0]
    else:
        logging.error(file_type.multiple_files_error_msg())
        exit()


def main():
    logging.basicConfig(
        stream=sys.stderr, format="[%(levelname)s]\t%(message)s", level=logging.DEBUG
    )

    markdown_file = get_file(Markdown, required=True, recursive=False)
    converter = Converter(
        markdown_file,
        citation_file=get_file(Bibliography, reference_file=markdown_file),
        template_file=get_file(Template, reference_file=markdown_file),
    )

    converted_file = converter.convert()
    if sys.stdout.isatty():
        pyperclip.copy(converted_file)
    else:
        print(converted_file)


if __name__ == "__main__":
    main()
