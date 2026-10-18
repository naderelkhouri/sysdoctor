"""
Testes para o módulo SystemCleaner e limpezas avançadas de caches.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from sysdoctor.core.cleaner import SystemCleaner, get_target_user_home


class TestSystemCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = SystemCleaner(dry_run=True)

    def test_get_target_user_home_default(self):
        home = get_target_user_home()
        self.assertIsInstance(home, Path)

    @patch("sysdoctor.core.cleaner.command_exists")
    @patch("sysdoctor.core.cleaner.run_command")
    def test_vacuum_journal_logs_success(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_run.return_value = (0, "Logs truncados", "")

        cleaner = SystemCleaner(dry_run=False)
        succ, msg = cleaner.vacuum_journal_logs("50M")
        self.assertTrue(succ)
        self.assertIn("Logs do journald truncados", msg)

    @patch("sysdoctor.core.cleaner.command_exists")
    @patch("sysdoctor.core.cleaner.run_command")
    def test_clean_dev_caches_dry_run(self, mock_run, mock_exists):
        mock_exists.side_effect = lambda cmd: cmd in ("uv", "pip", "npm")
        mock_run.return_value = (0, "Simulated", "")

        succ, msg = self.cleaner.clean_dev_caches()
        self.assertTrue(succ)
        self.assertIn("Caches de desenvolvimento limpos", msg)

    def test_clean_user_caches_dry_run(self):
        succ, msg = self.cleaner.clean_user_caches()
        self.assertTrue(succ)


if __name__ == "__main__":
    unittest.main()
