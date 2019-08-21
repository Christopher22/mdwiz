import unittest
import tempfile
from pathlib import Path

from mdwiz.converter import Converter


class TestConverter(unittest.TestCase):
    def setUp(self):
        self._tmp_directory_handle = tempfile.TemporaryDirectory()
        self.test_directory = Path(self._tmp_directory_handle.name)
        self.asset_document = TestConverter._copy_assets(
            self.test_directory, "example.md"
        )
        self.asset_bibliography = TestConverter._copy_assets(
            self.test_directory, "example.bib"
        )

    def tearDown(self):
        self._tmp_directory_handle.cleanup()

    def test_convert(self):
        converter = Converter(self.asset_document)
        result = converter.convert()
        self.assertIn("\section{A test.}", result)

    def test_bibliography(self):
        converter = Converter(self.asset_document, self.asset_bibliography)
        result = converter.convert()
        self.assertIn(r"\autocite{gundler}", result)

    @staticmethod
    def _copy_assets(destination: Path, file_name: str) -> Path:
        source = Path(__file__).parent / "data" / file_name
        assert source.is_file(), "Asset does not exist"

        destination = destination / file_name
        destination.write_text(source.read_text())
        return destination


if __name__ == "__main__":
    unittest.main()
