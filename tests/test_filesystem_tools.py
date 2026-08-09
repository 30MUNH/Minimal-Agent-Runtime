import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_runtime.filesystem_tools import build_filesystem_tools


class FilesystemToolTests(unittest.TestCase):
    def test_filesystem_write_and_read_are_real(self):
        with TemporaryDirectory() as directory:
            tools = {tool.name: tool for tool in build_filesystem_tools(Path(directory))}

            tools["write_file"].run({"path": "notes/todo.txt", "content": "TODO: ship it\n"})
            files = tools["list_files"].run({})
            content = tools["read_file"].run({"path": "notes/todo.txt"})

            self.assertIn("notes/todo.txt", files)
            self.assertEqual(content, "TODO: ship it\n")

    def test_search_files_finds_matching_lines(self):
        with TemporaryDirectory() as directory:
            tools = {tool.name: tool for tool in build_filesystem_tools(Path(directory))}
            tools["write_file"].run({"path": "a.txt", "content": "TODO: first\nok\n"})
            tools["write_file"].run({"path": "nested/b.txt", "content": "TODO: second\n"})

            matches = tools["search_files"].run({"query": "TODO"})

            self.assertEqual(
                matches,
                [
                    {"path": "a.txt", "line": 1, "text": "TODO: first"},
                    {"path": "nested/b.txt", "line": 1, "text": "TODO: second"},
                ],
            )

    def test_workspace_path_traversal_is_rejected(self):
        with TemporaryDirectory() as directory:
            tools = {tool.name: tool for tool in build_filesystem_tools(Path(directory))}

            with self.assertRaisesRegex(ValueError, "outside workspace"):
                tools["read_file"].run({"path": "../secret.txt"})

            with self.assertRaisesRegex(ValueError, "outside workspace"):
                tools["write_file"].run({"path": "/etc/passwd", "content": "nope"})
