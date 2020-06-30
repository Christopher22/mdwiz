from . import FileType


class Bibliography(FileType):
    def __init__(self):
        super().__init__("bib", "json")
