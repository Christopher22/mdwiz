import unittest
import tempfile
from pathlib import Path

from mdwiz.converter import Converter

from util import FileSystemUnitTest


class TestConverter(FileSystemUnitTest):
    def setUp(self):
        super().setUp()

        self.asset_document = TestConverter.copy_assets(
            self.test_directory, "example.md"
        )
        self.asset_bibliography = TestConverter.copy_assets(
            self.test_directory, "example.bib"
        )

    def test_convert(self):
        converter = Converter(self.asset_document)
        result = converter.convert()
        self.assertIn("\section{A test.}", result)

    def test_bibliography(self):
        converter = Converter(self.asset_document, self.asset_bibliography)
        result = converter.convert()
        self.assertIn(r"\autocite{gundler}", result)


if __name__ == "__main__":
    unittest.main()
