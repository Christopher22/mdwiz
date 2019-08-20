from typing import Sequence

from . import FileType


class Template(FileType):
    def file_extensions(self) -> Sequence[str]:
        return "tex"
