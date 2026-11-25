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

    @patch("sysdoctor.core.cleaner.command_exists")
    @patch("sysdoctor.core.cleaner.run_command")
    def test_clean_docker_containers_active(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_run.side_effect = [
            (0, "Docker running", ""),
            (0, "Deleted Containers: ... Total reclaimed space: 1.2GB", ""),
        ]

        cleaner = SystemCleaner(dry_run=False)
        succ, msg = cleaner.clean_docker_containers()
        self.assertTrue(succ)
        self.assertIn("Containers e imagens órfãs do Docker limpos", msg)

    @patch("sysdoctor.core.cleaner.command_exists")
    def test_clean_docker_containers_not_installed(self, mock_exists):
        mock_exists.return_value = False
        succ, msg = self.cleaner.clean_docker_containers()
        self.assertTrue(succ)
        self.assertIn("não instalado", msg)

    def test_clean_crash_reports_dry_run(self):
        succ, msg = self.cleaner.clean_crash_reports()
        self.assertTrue(succ)

    @patch("sysdoctor.core.cleaner.command_exists")
    @patch("sysdoctor.core.cleaner.run_command")
    def test_clean_flatpak_unused_installed(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_run.return_value = (0, "Runtimes removed", "")
        cleaner = SystemCleaner(dry_run=False)
        succ, msg = cleaner.clean_flatpak_unused()
        self.assertTrue(succ)
        self.assertIn("Flatpak removidos", msg)

    @patch("sysdoctor.core.cleaner.command_exists")
    def test_clean_flatpak_unused_not_installed(self, mock_exists):
        mock_exists.return_value = False
        succ, msg = self.cleaner.clean_flatpak_unused()
        self.assertTrue(succ)
        self.assertIn("não instalado", msg)

    @patch("sysdoctor.core.cleaner.command_exists")
    @patch("os.geteuid", return_value=0)
    @patch("psutil.virtual_memory")
    @patch("psutil.swap_memory")
    def test_recycle_swap_dry_run(self, mock_swap, mock_mem, mock_euid, mock_exists):
        mock_exists.return_value = True
        mock_mem.return_value = MagicMock(available=8 * 1024**3)
        mock_swap.return_value = MagicMock(used=2 * 1024**3)
        succ, msg = self.cleaner.recycle_swap()
        self.assertTrue(succ)
        self.assertIn("seriam executados", msg)


if __name__ == "__main__":
    unittest.main()
