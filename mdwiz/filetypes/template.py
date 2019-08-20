from . import FileType


class Template(FileType):
    def __init__(self, *args):
        super().__init__("tex")
