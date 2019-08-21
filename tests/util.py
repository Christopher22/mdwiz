import unittest
import tempfile
from pathlib import Path


class FileSystemUnitTest(unittest.TestCase):
    def setUp(self):
        self._tmp_directory_handle = tempfile.TemporaryDirectory()
        self.test_directory = Path(self._tmp_directory_handle.name)

    def tearDown(self):
        self._tmp_directory_handle.cleanup()

    @staticmethod
    def copy_assets(destination: Path, file_name: str) -> Path:
        source = Path(__file__).parent / "data" / file_name
        assert source.is_file(), "Asset does not exist"

        destination = destination / file_name
        destination.write_text(source.read_text())
        return destination
