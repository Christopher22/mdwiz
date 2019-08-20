import unittest
import tempfile
from pathlib import Path

from mdwiz.filetypes import FileType


class TestFileTypes(unittest.TestCase):
    def setUp(self):
        self._tmp_directory_handle = tempfile.TemporaryDirectory()
        self.test_directory = Path(self._tmp_directory_handle.name)

        # Add a valid file into the root
        (self.test_directory / "a.example").touch()

        # Add a valid file to a nested directory
        nested_directory = self.test_directory / "nested_directory"
        nested_directory.mkdir()
        (nested_directory / "b.example").touch()

        # Add rubbish
        (self.test_directory / "rubbi.sh").touch()

    def test_locate_files(self):
        example_filetype = FileType("example")

        self.assertEqual(
            len(example_filetype.locate_files(self.test_directory, recursive=False)), 1
        )
        self.assertEqual(
            len(example_filetype.locate_files(self.test_directory, recursive=True)), 2
        )

    def tearDown(self):
        self._tmp_directory_handle.cleanup()


if __name__ == "__main__":
    unittest.main()
