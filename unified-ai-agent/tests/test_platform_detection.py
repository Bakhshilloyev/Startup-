import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.adapters.common import arch
from agent.adapters import detect


class TestArch(unittest.TestCase):
    def test_normalize_x64(self):
        self.assertEqual(arch.normalize_arch("x86_64"), "x64")

    def test_normalize_arm(self):
        self.assertIn(arch.normalize_arch("aarch64"), ("aarch64", "arm64"))

    def test_bits(self):
        self.assertIn(arch.bits(), (32, 64))

    def test_summary_keys(self):
        s = arch.summary()
        for k in ("bits", "machine", "arch", "is_64bit", "python"):
            self.assertIn(k, s)


class TestPlatformDetect(unittest.TestCase):
    def test_detect_returns_platform(self):
        p = detect()
        self.assertTrue(hasattr(p, "name"))
        self.assertIn(p.name, ("linux", "windows", "termux", "macos", "base"))


if __name__ == "__main__":
    unittest.main()
