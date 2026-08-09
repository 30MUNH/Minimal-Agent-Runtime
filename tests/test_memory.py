import unittest

from agent_runtime import JsonMemory


class MemoryTests(unittest.TestCase):
    def test_memory_persists_values_between_instances(self):
        with self.subTest("json file reload"):
            from tempfile import TemporaryDirectory
            from pathlib import Path

            with TemporaryDirectory() as directory:
                path = Path(directory) / "memory.json"
                memory = JsonMemory(path)

                memory.remember("project", {"name": "runtime", "steps": 3})

                reloaded = JsonMemory(path)
                self.assertEqual(reloaded.recall("project"), {"name": "runtime", "steps": 3})
                self.assertEqual(reloaded.context(), {"project": {"name": "runtime", "steps": 3}})

    def test_memory_returns_default_for_missing_key(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as directory:
            memory = JsonMemory(Path(directory) / "memory.json")

            self.assertEqual(memory.recall("missing", default="fallback"), "fallback")


if __name__ == "__main__":
    unittest.main()
