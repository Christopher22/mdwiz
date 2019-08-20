from typing import Sequence

from . import FileType


class Bibliography(FileType):
    def file_extensions(self) -> Sequence[str]:
        return "bib"
