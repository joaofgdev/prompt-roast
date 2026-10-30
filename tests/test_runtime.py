import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from prompt_roast.runtime import build_runtime


class RuntimeTest(unittest.TestCase):
    def test_archive_runs_away_from_checkout_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = build_runtime(Path(tmp) / "out with spaces" / "prompt-roast.pyz")
            cmd = [sys.executable, str(archive), "evaluate", "--type", "request", "--p1", "3", "--p2", "3", "--p3", "3"]
            run = subprocess.run(cmd, cwd=tmp, text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(run.stdout)["score"], 10)

    def test_archive_can_install_itself_without_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = build_runtime(root / "source" / "prompt-roast.pyz")
            project = root / "demo project"
            project.mkdir()
            command = [sys.executable, str(archive), "install", "--agent", "codex", "--scope", "local", "--project", str(project)]
            result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, check=True)
            self.assertIn("Instalação concluída", result.stdout)
            self.assertIn("ainda não foi testada", result.stdout)
            result = subprocess.run(command + ["--json"], cwd=tmp, capture_output=True, text=True, check=True)
            installed = Path(json.loads(result.stdout)["runtime"])
            doctor = subprocess.run([sys.executable, str(archive), "doctor", "--agent", "codex", "--scope", "local", "--project", str(project)], cwd=tmp, capture_output=True, text=True, check=True)
            self.assertIn("instalação preparada", doctor.stdout)
            self.assertIn("ainda não foi verificado", doctor.stdout)
            archive.unlink()
            result = subprocess.run([sys.executable, str(installed), "evaluate", "--type", "request", "--p1", "3", "--p2", "3", "--p3", "3"], cwd=tmp, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["score"], 10)
