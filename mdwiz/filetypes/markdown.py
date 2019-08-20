from . import FileType


class Markdown(FileType):
    def __init__(self, *args):
        super().__init__(
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
