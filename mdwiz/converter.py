import logging
import subprocess
import tempfile
import shutil
from collections.abc import MutableSet
from pathlib import Path
from shlex import quote
from typing import Optional, Sequence


class Converter(MutableSet):
    class PandocException(Exception):
        def __init__(self, msg: str, status_code: int):
            super().__init__(msg)
            self.status_code = status_code

    def __init__(
        self,
        markdown_file: Path,
        citation_file: Optional[Path] = None,
        template_file: Optional[Path] = None,
    ):
        self._parameters = set()

        if not markdown_file.is_file():
            raise ValueError("Markdown file does not exists!")
        self.markdown_file = str(markdown_file.absolute())

        self.add("--from=markdown+smart+tex_math_dollars")
        self.add("--to=latex")
        self.add("--standalone")

        # Add citation processing
        self.citation_file = Converter._prepare_path(citation_file, markdown_file)
        if self.citation_file is not None:
            self.add("--biblatex")
            self.add(f"--bibliography={quote(self.citation_file)}")

        # Add custom template
        self.template_file = Converter._prepare_path(template_file, markdown_file)
        if self.template_file is not None:
            self.add(f"--template={quote(self.template_file)}")

    def __contains__(self, value: str):
        return value in self._parameters

    def __iter__(self):
        return iter(self._parameters)

    def __len__(self):
        return len(self._parameters)

    def add(self, value: str):
        self._parameters.add(value)

    def discard(self, value: str):
        self._parameters.discard(value)

    def convert(self) -> str:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "output.tex"
            result = subprocess.run(
                [
                    "pandoc",
                    *tuple(self._parameters),
                    "-o",
                    str(output_file),
                    str(self.markdown_file),
                ],
                capture_output=True,
                shell=False,
                text=True,
            )

            if result.returncode != 0:
                raise Converter.PandocException(result.stderr, result.returncode)

            return output_file.read_text()

    @staticmethod
    def _prepare_path(
        input_path: Optional[Path], reference_path: Path
    ) -> Optional[str]:
        if input_path is None or not input_path.is_file():
            return None

        # Make files relative to the folder rather to the file
        if reference_path.is_file():
            reference_path = reference_path.parent

        return str(input_path.relative_to(reference_path))

    @staticmethod
    def is_available() -> bool:
        return shutil.which("pandoc") is not None
