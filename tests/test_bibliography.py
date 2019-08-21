import unittest
import tempfile
from pathlib import Path

from mdwiz.bibliography import Bibliography
from mdwiz.converter import Converter

from util import FileSystemUnitTest


class TestBibliography(FileSystemUnitTest):
    def setUp(self):
        super().setUp()

        self.asset_document = TestBibliography.copy_assets(
            self.test_directory, "example.md"
        )
        self.asset_bibliography = TestBibliography.copy_assets(
            self.test_directory, "example.bib"
        )

    def test_ids(self):
        bibliography = Bibliography.from_file(self.asset_bibliography)
        self.assertCountEqual(
            tuple(bibliography.keys()), ["gundler", "doe", "unused-doe"]
        )

    def test_find_references(self):
        converter = Converter(self.asset_document, self.asset_bibliography)
        used_citations = Bibliography.used_citations(converter.convert())
        self.assertCountEqual(used_citations, ["gundler", "doe", "unknown_reference"])

    def test_find_missing_references(self):
        bibliography = Bibliography.from_file(self.asset_bibliography)
        converter = Converter(self.asset_document, self.asset_bibliography)
        missing_citations = bibliography.find_missing_citations(converter.convert())
        self.assertCountEqual(missing_citations, ["unknown_reference"])


if __name__ == "__main__":
    unittest.main()
