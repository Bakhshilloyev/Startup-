import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.memory.sqlite_store import SQLiteStore


class TestMemory(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.store = SQLiteStore(self.path)

    def tearDown(self):
        self.store.close()
        os.remove(self.path)

    def test_put_get(self):
        self.store.put("k", "v")
        self.assertEqual(self.store.get("k"), "v")

    def test_search(self):
        self.store.put("project:goat", "terminal agent")
        rows = self.store.search("goat")
        self.assertEqual(len(rows), 1)

    def test_delete(self):
        self.store.put("k", "v")
        self.store.delete("k")
        self.assertIsNone(self.store.get("k"))


if __name__ == "__main__":
    unittest.main()
