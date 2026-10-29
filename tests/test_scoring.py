import unittest
from prompt_roast.scoring import CAPS, evaluate


class ScoringTest(unittest.TestCase):
    def test_maximums(self):
        self.assertEqual(evaluate("request", 3, 3, 3)["score"], 10)
        self.assertEqual(evaluate("question", 3, 3, 3, butler=True)["score"], 9)

    def test_caps(self):
        for pattern, cap in CAPS.items():
            with self.subTest(pattern=pattern):
                self.assertEqual(evaluate("request", 3, 3, 3, pattern)["score"], cap)

    def test_invalid_inputs(self):
        for args in [("bad", 1, 1, 1), ("request", -1, 1, 1),
                     ("request", 4, 1, 1), ("request", True, 1, 1),
                     ("request", 1.0, 1, 1), ("request", 1, 1, 1, "bad")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                evaluate(*args)

    def test_weakest_pillar(self):
        self.assertEqual(evaluate("question", 2, 0, 1)["weakest"], "scope")

class CliTest(unittest.TestCase):
    def test_json_and_errors(self):
        import json
        import subprocess
        import sys
        cmd = [sys.executable, "-m", "prompt_roast", "evaluate", "--type", "request", "--p1", "3", "--p2", "3", "--p3", "3"]
        good = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(good.returncode, 0)
        self.assertEqual(json.loads(good.stdout)["score"], 10)
        for extra in (["--pattern", "bad"], ["--type", "bad"], ["--p1", "4"]):
            bad = subprocess.run(cmd + extra, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(bad.stdout, "")
            self.assertTrue(bad.stderr)
