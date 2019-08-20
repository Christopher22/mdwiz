from pathlib import Path
from typing import Sequence, Optional


class FileType:
    def __init__(self, *args):
        self.extensions = tuple(args)

    def locate_files(
        self, root: Path, reference_file: Optional[Path] = None, recursive: bool = True
    ) -> Sequence[Path]:
        # Generate all the candidate files
        candidates = []
        for extension in self.file_extensions():
            extension = f"*.{extension}"
            candidates.extend(
                root.rglob(extension) if recursive else root.glob(extension)
            )

        # If more than one candiate is availailable, try to find its stem
        if len(candidates) > 1 and reference_file is not None:
            for candidate in candidates:
                if candidate.stem == reference_file.stem:
                    return (candidate,)

        return candidates

    def multiple_files_error_msg(self) -> str:
        return f"Multiple suitable {self.__class__.__name__} files were found. Please specify explicitely."

    def missing_file_error_msg(self) -> str:
        return f"No file matching the required type for {self.__class__.__name__} was found."

    def file_extensions(self) -> Sequence[str]:
        return self.extensions
