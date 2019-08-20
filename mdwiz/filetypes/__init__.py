from pathlib import Path
from typing import Sequence, Optional


class FileType:
    def locate_files(
        self, root: Path, reference_file: Optional[Path] = None
    ) -> Sequence[Path]:
        # Generate all the candidate files
        candidates = []
        for extension in self.file_extensions():
            candidates.extend(root.rglob(f"*.{extension}"))

        # If more than one candiate is availailable, try to find its stem
        if len(candidates) > 1 and reference_file is not None:
            for candidate in candidates:
                if candidate.stem == reference_file.stem:
                    return (candidate,)

        return candidates

    def file_extensions(self) -> Sequence[str]:
        raise NotImplementedError()
