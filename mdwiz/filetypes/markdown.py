from typing import Sequence

from . import FileType


class Markdown(FileType):
    def file_extensions(self) -> Sequence[str]:
        return (
            "markdown",
            "mdown",
            "mkdn",
            "md",
            "mkd",
            "mdwn",
            "mdtxt",
            "mdtext",
            "text",
            "Rmd",
        )
