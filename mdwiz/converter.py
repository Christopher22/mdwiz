import re
import shutil
import subprocess
import sys
import tempfile
import warnings
from collections.abc import MutableSequence
from pathlib import Path
from typing import Optional, FrozenSet, Union, Sequence

from mdwiz.bibliography import Bibliography


class Converter(MutableSequence):
    class PandocException(Exception):
        def __init__(self, msg: str, status_code: int):
            super().__init__(msg)
            self.status_code = status_code

    class MissingReferenceWarning(RuntimeWarning):
        def __init__(self, missing_references: FrozenSet[str]):
            super().__init__()
            self.missing_references = missing_references

        def __str__(self):
            return f"Missing references: {', '.join(self.missing_references)}"

        @staticmethod
        def check_references(
                citation_file: Union[Path, str], latex_code: str, cwd: Optional[str] = None
        ):
            bibliography = Bibliography.from_file(citation_file, cwd=cwd)
            missing_references = bibliography.find_missing_citations(latex_code)

            if len(missing_references) > 0:
                warnings.warn(Converter.MissingReferenceWarning(missing_references))

    def __init__(
            self,
            markdown_files: Sequence[Path],
            citation_file: Optional[Path] = None,
            template_file: Optional[Path] = None,
            csl_file: Optional[Path] = None,
    ):
        self._parameters = [
            "--from=markdown+smart+tex_math_dollars",
            "--to=latex",
            "--standalone",
            "--listings",
            "--filter=pandoc-xnos",
            "--filter=pantable",
            "--table-of-contents",
        ]

        if len(markdown_files) == 0 or not all(
                file.is_file() for file in markdown_files
        ):
            raise ValueError("Markdown file does not exists!")
        self.markdown_files = [
            file.absolute() for file in Converter._sort_files(markdown_files)
        ]
        self.csl_file = csl_file

        # Add citation processing
        self.citation_file = Converter._prepare_path(
            citation_file, self.markdown_files[0]
        )
        if self.citation_file is not None:
            if csl_file is not None:
                self.append(f"--csl={self.csl_file}")
            if Bibliography.get_type(self.citation_file) == Bibliography.BibType.BibTex:
                self.append("--biblatex")
            self.append(f"--bibliography={self.citation_file}")

        # Add custom template
        self.template_file = Converter._prepare_path(
            template_file, self.markdown_files[0]
        )
        if self.template_file is not None:
            self.append(f"--template={self.template_file}")

    def __contains__(self, value: str):
        return value in self._parameters

    def __iter__(self):
        return iter(self._parameters)

    def __len__(self):
        return len(self._parameters)

    def __getitem__(self, item: int) -> str:
        return self._parameters[item]

    def __setitem__(self, key: int, value: str):
        self._parameters[key] = value

    def __delitem__(self, key: int):
        del self._parameters[key]

    def insert(self, index: int, element: str):
        self._parameters.insert(index, element)

    def convert(self) -> str:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "output.tex"
            result = subprocess.run(
                [
                    "pandoc",
                    *self._parameters,
                    "-o",
                    str(output_file),
                    *[str(file) for file in self.markdown_files],
                ],
                capture_output=True,
                shell=False,
                text=True,
                cwd=str(self.markdown_files[0].parent),
            )

            if result.returncode != 0:
                raise Converter.PandocException(result.stderr, result.returncode)
            latex_output = output_file.read_text(encoding="utf-8")

            # Check references, if specified
            if self.citation_file is not None:
                Converter.MissingReferenceWarning.check_references(
                    self.citation_file,
                    latex_output,
                    cwd=str(self.markdown_files[0].parent),
                )

            return latex_output

    @staticmethod
    def is_available() -> bool:
        return shutil.which("pandoc") is not None

    @staticmethod
    def _prepare_path(
            input_path: Optional[Path], reference_path: Path
    ) -> Optional[str]:
        if input_path is None or not input_path.is_file():
            return None

        try:
            output_path = str(input_path.absolute().relative_to(reference_path.parent))
        except ValueError:
            output_path = str(input_path)

        return output_path

    @staticmethod
    def _sort_files(files: Sequence[Path]) -> Sequence[Path]:
        """
        Sort the given files if they start with a number.

        >>> [f.stem for f in Converter._sort_files([Path('3_file'), Path('0-file'), Path('2 file'), Path('last file')])]
        ['0-file', '2 file', '3_file', 'last file']

        :param files: The files which
        :return: The files sorted by their stem.
        """
        order_extractor = re.compile(r"^([0-9]+)")
        ids = [order_extractor.match(file.stem) for file in files]
        ids = [
            int(detected_id[1]) if detected_id is not None else sys.maxsize
            for detected_id in ids
        ]

        ids, files = zip(*sorted(zip(ids, files)))
        return files
