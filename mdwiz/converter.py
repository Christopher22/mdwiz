import shutil
import subprocess
import tempfile
import warnings
from collections.abc import MutableSequence
from pathlib import Path
from typing import Optional, FrozenSet, Union

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
            markdown_file: Path,
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

        if not markdown_file.is_file():
            raise ValueError("Markdown file does not exists!")
        self.markdown_file = markdown_file.absolute()
        self.csl_file = csl_file

        # Add citation processing
        self.citation_file = Converter._prepare_path(citation_file, markdown_file)
        if self.citation_file is not None:
            if csl_file is not None:
                self.append(f"--cls={self.csl_file}")
            if Bibliography.get_type(self.citation_file) == Bibliography.BibType.BibTex:
                self.append("--biblatex")
            self.append(f"--bibliography={self.citation_file}")

        # Add custom template
        self.template_file = Converter._prepare_path(template_file, markdown_file)
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
                    str(self.markdown_file),
                ],
                capture_output=True,
                shell=False,
                text=True,
                cwd=str(self.markdown_file.parent),
            )

            if result.returncode != 0:
                raise Converter.PandocException(result.stderr, result.returncode)
            latex_output = output_file.read_text(encoding="utf-8")

            # Check references, if specified
            if self.citation_file is not None:
                Converter.MissingReferenceWarning.check_references(
                    self.citation_file, latex_output, cwd=str(self.markdown_file.parent)
                )

            return latex_output

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
    def is_available() -> bool:
        return shutil.which("pandoc") is not None
