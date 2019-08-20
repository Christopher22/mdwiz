from pathlib import Path
from typing import Optional, Sequence
import logging
import tempfile

import pypandoc


class Converter:
    def __init__(
        self,
        markdown_file: Path,
        citation_file: Optional[Path],
        template_file: Optional[Path],
    ):
        if not markdown_file.is_file():
            raise ValueError("Markdown file does not exists!")

        self.markdown_file = str(markdown_file.absolute())
        self.citation_file = Converter._prepare_path(citation_file)
        self.template_file = Converter._prepare_path(template_file)

    def convert(self, *args) -> str:
        additional_parameters = list(*args)

        # Add citation processing
        if self.citation_file is not None:
            additional_parameters.append("--biblatex")
            additional_parameters.append(f'--bibliography="{self.citation_file}"')

        # Add custom template
        additional_parameters.append("-s")
        if self.template_file is not None:
            additional_parameters.append(f'--template="{self.template_file}"')

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "output.tex"
            pypandoc.convert_file(
                str(self.markdown_file),
                "latex",
                format="md",
                outputfile=str(output_file),
                extra_args=additional_parameters,
            )
            return output_file.read_text()

    @staticmethod
    def _prepare_path(input_path: Optional[Path]) -> Optional[str]:
        if input_path is None or not input_path.is_file():
            return None
        return str(input_path.absolute())
