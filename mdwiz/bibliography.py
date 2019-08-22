from pathlib import Path
from typing import Set
import shutil
import subprocess
import json
import re


class Bibliography(dict):
    def find_missing_citations(self, latex_code: str) -> Set[str]:
        used_references = Bibliography.used_citations(latex_code)
        available_references = frozenset(self.keys())
        return used_references.difference(available_references)

    @staticmethod
    def used_citations(latex_code: str) -> Set[str]:
        citation_regex = re.compile(r"\\[a-z]+cite{([^}]+)")
        return {
            citation.group(1).strip()
            for citation in citation_regex.finditer(latex_code)
        }

    @staticmethod
    def from_file(bibliography: Path) -> "Bibliography":
        parsed_data = subprocess.run(
            ["pandoc-citeproc", "--bib2json", str(bibliography)],
            capture_output=True,
            shell=False,
            text=True,
        )

        if parsed_data.returncode != 0:
            raise RuntimeError(parsed_data.stderr)
        else:
            parsed_data = json.loads(parsed_data.stdout)

        return Bibliography([(citation["id"], citation) for citation in parsed_data])

    @staticmethod
    def is_available() -> bool:
        return shutil.which("pandoc-citeproc") is not None
