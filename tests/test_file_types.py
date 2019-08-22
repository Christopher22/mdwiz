import unittest
import tempfile
from pathlib import Path

from mdwiz.filetypes import FileType

from util import FileSystemUnitTest


class TestFileTypes(FileSystemUnitTest):
    def setUp(self):
        super().setUp()

        # Add a valid file into the root
        (self.test_directory / "a.example").touch()
        (self.test_directory / "a.second_example").touch()

        # Add files to a nested directory
        nested_directory = self.test_directory / "nested_directory"
        nested_directory.mkdir()

        b_example = nested_directory / "b.example"
        b_example.touch()
        b_example.write_text("This is an example!")
        (nested_directory / "b.second_example").touch()

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

    def test_reference_file(self):
        example_filetype = FileType("second_example")

        self.assertEqual(
            len(example_filetype.locate_files(self.test_directory, recursive=True)), 2
        )

        self.assertEqual(
            len(
                example_filetype.locate_files(
                    self.test_directory,
                    reference_file=(self.test_directory / "a.example"),
                    recursive=True,
                )
            ),
            1,
        )

    def test_filesize_threshold(self):
        example_filetype = FileType("example")

        self.assertEqual(
            len(example_filetype.locate_files(self.test_directory, recursive=True)), 2
        )

        self.assertEqual(
            len(
                example_filetype.locate_files(
                    self.test_directory, recursive=True, min_size=5
                )
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
