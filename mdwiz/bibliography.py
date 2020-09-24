import json
import re
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import FrozenSet, Union, Iterable, Optional


class Bibliography(dict):
    class BibType(Enum):
        BibTex = 0
        Csl = 1

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.value == other.value
            return False

    @staticmethod
    def get_type(path: str) -> BibType:
        if path.endswith(".json") or path.endswith(".js"):
            return Bibliography.BibType.Csl
        elif path.endswith(".bib"):
            return Bibliography.BibType.BibTex
        else:
            raise ValueError("Unknown file extension")

    def find_missing_citations(self, latex_code: str) -> FrozenSet[str]:
        used_references = frozenset(Bibliography.used_citations(latex_code))
        available_references = frozenset(self.keys())
        return used_references.difference(available_references)

    @staticmethod
    def used_citations(latex_code: str) -> Iterable[str]:
        citation_regex = re.compile(r"\\[a-z]+cite{([^}]+)")
        for citation in citation_regex.finditer(latex_code):
            citation = citation.group(1).strip()
            for value in citation.split(","):
                yield value.strip()

    @staticmethod
    def from_file(
            bibliography: Union[Path, str], cwd: Optional[str] = None
    ) -> "Bibliography":
        bibliography = (
            bibliography if isinstance(bibliography, Path) else Path(bibliography)
        )
        if bibliography.suffix == ".bib":
            parsed_data = subprocess.run(
                ["pandoc-citeproc", "--bib2json", str(bibliography)],
                capture_output=True,
                shell=False,
                text=True,
                encoding="utf-8",
                cwd=cwd,
            )

            if parsed_data.returncode != 0:
                raise RuntimeError(parsed_data.stderr)
            else:
                parsed_data = json.loads(parsed_data.stdout, encoding="utf-8")
        elif bibliography.suffix == ".json":
            with bibliography.open("r", encoding="utf-8") as json_file:
                parsed_data = json.load(json_file)
        else:
            raise NotImplementedError(
                f"Software does not know how to parse bibliography with extension '{bibliography.suffix}'"
            )

        return Bibliography([(citation["id"], citation) for citation in parsed_data])

    @staticmethod
    def is_available() -> bool:
        return shutil.which("pandoc-citeproc") is not None
