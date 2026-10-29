import json
import os
import tempfile
import unittest
from unittest.mock import patch
from prompt_roast import state


class StateTest(unittest.TestCase):
    def test_sessions_are_separate_and_private(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"PROMPT_ROAST_STATE_DIR": temp}):
            one = state.new_session("codex", temp)["session"]
            two = state.new_session("codex", temp)["session"]
            three = state.new_session("cursor", temp)["session"]
            paths = [state.path_for("codex", temp, one), state.path_for("codex", temp, two), state.path_for("cursor", temp, three)]
            self.assertEqual(len(set(paths)), 3)
            self.assertNotEqual(state.path_for("codex", temp, one), state.path_for("codex", temp + "/other", one))
            self.assertEqual(json.loads(paths[0].read_text())["scores"], [])
            self.assertNotIn(temp, paths[0].read_text())
            if os.name != "nt":
                self.assertEqual(paths[0].stat().st_mode & 0o777, 0o600)

    def test_record_idempotent_conflict_and_corruption(self):
        from prompt_roast.scoring import evaluate
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"PROMPT_ROAST_STATE_DIR": temp}):
            session = state.new_session("codex", temp)["session"]
            path = state.path_for("codex", temp, session)
            first = evaluate("request", 1, 2, 3)
            state.record("codex", temp, session, "event-1", first)
            state.record("codex", temp, session, "event-1", first)
            self.assertEqual(len(json.loads(path.read_text())["scores"]), 1)
            with self.assertRaises(ValueError):
                state.record("codex", temp, session, "event-1", evaluate("request", 3, 2, 3))
            path.write_text("{broken")
            with self.assertRaises(ValueError):
                state.record("codex", temp, session, "event-2", first)
            self.assertEqual(path.read_text(), "{broken")

    def test_concurrent_and_failed_write(self):
        from concurrent.futures import ThreadPoolExecutor
        from prompt_roast.scoring import evaluate
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"PROMPT_ROAST_STATE_DIR": temp}):
            session = state.new_session("codex", temp)["session"]
            path = state.path_for("codex", temp, session)
            score = evaluate("question", 1, 2, 3)
            with ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(lambda i: state.record("codex", temp, session, str(i), score), range(20)))
            self.assertEqual(len(json.loads(path.read_text())["scores"]), 20)
            before = path.read_bytes()
            with patch("os.replace", side_effect=OSError("falha")):
                with self.assertRaises(OSError):
                    state.record("codex", temp, session, "new", score)
            self.assertEqual(path.read_bytes(), before)

    def test_statistics(self):
        from prompt_roast.scoring import evaluate
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"PROMPT_ROAST_STATE_DIR": temp}):
            session = state.new_session("codex", temp)["session"]
            empty = state.statistics("codex", temp, session)
            self.assertEqual((empty["count"], empty["average"], empty["trend"]), (0, None, None))
            for index, score in enumerate((4, 7, 9)):
                points = {4: (1, 1, 1), 7: (2, 2, 2), 9: (3, 3, 2)}[score]
                state.record("codex", temp, session, str(index), evaluate("request", *points))
                if index == 1:
                    self.assertIsNone(state.statistics("codex", temp, session)["trend"])
            stats = state.statistics("codex", temp, session)
            self.assertEqual((stats["count"], stats["average"], stats["recent"], stats["trend"]), (3, 6.7, [4, 7, 9], "improving"))
            for index in range(3, 7):
                state.record("codex", temp, session, str(index), evaluate("request", 0, 0, 0))
            self.assertEqual(len(state.statistics("codex", temp, session)["recent"]), 5)

    def test_reset_and_savage_are_isolated(self):
        from prompt_roast.scoring import evaluate
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"PROMPT_ROAST_STATE_DIR": temp}):
            a = state.new_session("codex", temp)["session"]
            b = state.new_session("codex", temp)["session"]
            for session in (a, b):
                state.record("codex", temp, session, "event", evaluate("request", 1, 1, 1))
            state.savage("codex", temp, a, True)
            self.assertEqual(state.statistics("codex", temp, b)["tone"], "normal")
            state.reset("codex", temp, a)
            self.assertEqual(state.statistics("codex", temp, a)["tone"], "savage")
            self.assertEqual(state.statistics("codex", temp, a)["count"], 0)
            self.assertEqual(state.statistics("codex", temp, b)["count"], 1)
            state.savage("codex", temp, a, False)
            self.assertEqual(state.statistics("codex", temp, a)["tone"], "normal")

    def test_windows_lock_uses_platform_locking(self):
        import sys
        from types import SimpleNamespace
        from unittest.mock import Mock
        lock = Mock()
        lock.fileno.return_value = 42
        windows = SimpleNamespace(LK_LOCK=1, locking=Mock())
        with patch.object(sys, "platform", "win32"), patch.dict(sys.modules, {"msvcrt": windows}):
            state.lock_session_file(lock)
        lock.seek.assert_called_once_with(0)
        windows.locking.assert_called_once_with(42, 1, 1)
