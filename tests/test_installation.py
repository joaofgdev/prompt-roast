import tempfile
import unittest
from pathlib import Path
from prompt_roast.integrations import START, END, block_content, remove_block, check_path


class ManagedBlocksTest(unittest.TestCase):
    def test_existing_rules_preserved(self):
        old = b"# Minhas regras\nnao alterar\n"
        block = START + b"\ninstrucoes\n" + END
        result = block_content(old, block)
        self.assertEqual(block_content(result, block), result)
        self.assertEqual(remove_block(result, block), old)

    def test_invalid_or_modified_markers_are_rejected(self):
        block = START + b"\ninstrucoes\n" + END
        with self.assertRaises(ValueError):
            block_content(START, block)
        with self.assertRaises(ValueError):
            remove_block(START + b"alterado" + END, block)

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "outside").mkdir()
            (root / "link").symlink_to(root / "outside")
            with self.assertRaises(ValueError):
                check_path(root / "link" / "file")

    def test_install_all_reinstall_partial_uninstall(self):
        import json
        from prompt_roast.integrations import install, uninstall
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = b"# Regras pessoais\nMantenha isso.\n"
            (root / "AGENTS.md").write_bytes(old)
            result = install("all", "local", root)
            self.assertEqual(len(result["prepared"]), 5)
            runtime = Path(result["runtime"])
            self.assertTrue(runtime.is_file())
            self.assertEqual((root / "AGENTS.md").read_bytes().count(START), 1)
            self.assertEqual(len(list((root / ".agents/skills").rglob("SKILL.md"))), 8)
            install("all", "local", root)
            self.assertEqual((root / "AGENTS.md").read_bytes().count(START), 1)
            uninstall("codex", "local", root)
            self.assertEqual((root / "AGENTS.md").read_bytes(), old)
            self.assertTrue(runtime.exists())
            self.assertTrue((root / ".agents/skills/prompt-roast/SKILL.md").exists())
            uninstall("all", "local", root)
            self.assertFalse(runtime.exists())
            self.assertEqual((root / "AGENTS.md").read_bytes(), old)

    def test_collision_and_modified_files_are_preserved(self):
        from prompt_roast.integrations import install, uninstall
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rule = root / ".cursor/rules/prompt-roast.mdc"
            rule.parent.mkdir(parents=True)
            rule.write_text("minha regra")
            with self.assertRaises(ValueError):
                install("cursor", "local", root)
            self.assertEqual(rule.read_text(), "minha regra")
            rule.unlink()
            install("cursor", "local", root)
            rule.write_text("modificado pelo usuario")
            result = uninstall("cursor", "local", root)
            self.assertIn(str(rule), result["preserved"])
            self.assertEqual(rule.read_text(), "modificado pelo usuario")

    def test_global_codex_paths_and_cursor_pending(self):
        import os
        from unittest.mock import patch
        from prompt_roast.integrations import install
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custom = root / "my-codex"
            with patch.dict(os.environ, {"HOME": tmp, "CODEX_HOME": str(custom), "XDG_DATA_HOME": str(root / "data")}, clear=False):
                result = install("codex", "global")
                self.assertTrue((root / ".agents/skills/prompt-roast/SKILL.md").is_file())
                self.assertIn("prompt-roast:start", (custom / "AGENTS.md").read_text())
                self.assertTrue(Path(result["runtime"]).is_file())
                result = install("cursor", "global")
                self.assertTrue(result["pending"])
                self.assertFalse(result["host_tested"])

    def test_doctor_distinguishes_prepared_from_verified(self):
        import os
        from unittest.mock import patch
        from prompt_roast.integrations import doctor, install
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            with patch.dict(os.environ, {"HOME": tmp, "XDG_DATA_HOME": str(root / "data"), "PROMPT_ROAST_STATE_DIR": str(root / "state")}):
                self.assertFalse(doctor("codex", "local", project)["agents"]["codex"]["prepared"])
                install("all", "local", project)
                result = doctor("all", "local", project)
                self.assertTrue(result["runtime_ok"])
                self.assertTrue(result["agents"]["codex"]["prepared"])
                self.assertFalse(result["agents"]["codex"]["host_tested"])
                with patch("shutil.which", return_value=None):
                    self.assertIsNone(doctor("claude", "local", project)["agents"]["claude"]["executable"])
                Path(result["runtime"]).unlink()
                self.assertIsNone(doctor("codex", "local", project)["runtime_ok"])
                install("cursor", "global")
                self.assertTrue(doctor("cursor", "global")["agents"]["cursor"]["pending"])

    def test_native_manifests_commands_and_rules(self):
        import json
        import tomllib
        from prompt_roast.integrations import install
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install("all", "local", root)
            bundle = root / ".prompt-roast/bundles"
            codex = bundle / "codex/prompt-roast"
            self.assertEqual(json.loads((codex / ".codex-plugin/plugin.json").read_text())["name"], "prompt-roast")
            self.assertTrue((codex / "skills/prompt-roast/SKILL.md").is_file())
            claude = bundle / "claude/prompt-roast"
            self.assertEqual(json.loads((claude / ".claude-plugin/plugin.json").read_text())["name"], "prompt-roast")
            self.assertIn("SessionStart", json.loads((claude / "hooks/hooks.json").read_text())["hooks"])
            gemini = bundle / "gemini/prompt-roast"
            self.assertEqual(json.loads((gemini / "gemini-extension.json").read_text())["name"], "prompt-roast")
            for operation in ("score", "reset", "help", "setup-global", "setup-local", "savage"):
                self.assertTrue((claude / "commands" / (operation + ".md")).is_file())
                for path in (root / ".gemini/commands/prompt-roast" / (operation + ".toml"), gemini / "commands/prompt-roast" / (operation + ".toml")):
                    self.assertTrue(tomllib.loads(path.read_text())["prompt"])
            self.assertIn("alwaysApply: true", (root / ".cursor/rules/prompt-roast.mdc").read_text())
            self.assertIn("trigger: always_on", (root / ".agents/rules/prompt-roast.md").read_text())

    def test_menu_actions_are_installed_and_removed(self):
        import os
        from unittest.mock import patch
        from prompt_roast.integrations import install, uninstall
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.dict(os.environ, {"HOME": tmp, "XDG_DATA_HOME": str(root / "data")}):
                install("all", "global")
                for action in ("score", "reset", "help", "savage-on", "savage-off", "setup-global", "setup-local"):
                    for path in (root / ".agents/skills" / ("prompt-roast-" + action) / "SKILL.md", root / ".cursor/commands" / ("prompt-roast-" + action + ".md"), root / ".gemini/config/global_workflows" / ("prompt-roast-" + action + ".md"), root / ".claude/commands/prompt-roast" / (action + ".md"), root / ".gemini/commands/prompt-roast" / (action + ".toml")):
                        self.assertTrue(path.is_file(), str(path))
                install("all", "global")
                uninstall("all", "global")
                self.assertFalse((root / ".agents/skills/prompt-roast-score/SKILL.md").exists())
                self.assertFalse((root / ".cursor/commands/prompt-roast-score.md").exists())
                self.assertFalse((root / ".gemini/config/global_workflows/prompt-roast-score.md").exists())

    def test_uninstall_preserves_file_without_final_newline(self):
        from prompt_roast.integrations import install, uninstall
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = b"# Regra sem quebra de linha"
            (root / "AGENTS.md").write_bytes(original)
            install("codex", "local", root)
            install("codex", "local", root)
            uninstall("codex", "local", root)
            self.assertEqual((root / "AGENTS.md").read_bytes(), original)

    def test_bundles_include_licenses(self):
        from prompt_roast.integrations import install
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install("all", "local", root)
            for agent in ("codex", "claude", "gemini"):
                bundle = root / ".prompt-roast/bundles" / agent / "prompt-roast"
                self.assertIn("MIT License", (bundle / "LICENSE").read_text())
                self.assertIn("Copyright (c) 2025", (bundle / "THIRD_PARTY_NOTICES.md").read_text())

    def test_windows_rule_quotes_paths_for_powershell_and_bash(self):
        import sys
        from unittest.mock import patch
        from prompt_roast.integrations import _layout
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(sys, "platform", "win32"), patch.object(sys, "executable", "C:\\Users\\Ana Maria\\python.exe"):
                _, rule = _layout("claude", "local", tmp, Path(tmp) / "runtime name.pyz", b"skill", b"rubrica")
            self.assertIn("PowerShell execute `& 'C:\\Users\\Ana Maria\\python.exe'", rule)
            self.assertIn("Git Bash execute", rule)
            self.assertIn("runtime name.pyz'", rule)
