"""
Testes para o gerenciador de pacotes Snap.
"""

import unittest
from unittest.mock import patch
from sysdoctor.package_managers.snap import SnapPackageManager


class TestSnapPackageManager(unittest.TestCase):
    def setUp(self):
        self.snap = SnapPackageManager()

    @patch("sysdoctor.package_managers.snap.command_exists")
    @patch("sysdoctor.package_managers.snap.run_command")
    def test_get_disabled_revisions_handles_composite_notes(self, mock_run, mock_exists):
        mock_exists.return_value = True
        fake_snap_output = (
            "Name         Version    Rev   Tracking       Publisher   Notes\n"
            "antigravity  2.25.0     54    latest/stable  canonical   disabled,classic\n"
            "code         6d62b1d5   271   latest/stable  vscode      disabled,classic\n"
            "core22       20260824   2955  latest/stable  canonical   base,disabled\n"
            "firefox      130.0      4800  latest/stable  mozilla     -\n"
            "vlc          3.0.20     3721  latest/stable  videolan    disabled\n"
        )
        mock_run.return_value = (0, fake_snap_output, "")

        disabled = self.snap.get_disabled_revisions()
        self.assertEqual(len(disabled), 4)
        self.assertIn(("antigravity", "54"), disabled)
        self.assertIn(("code", "271"), disabled)
        self.assertIn(("core22", "2955"), disabled)
        self.assertIn(("vlc", "3721"), disabled)

    @patch("sysdoctor.package_managers.snap.command_exists")
    @patch("sysdoctor.package_managers.snap.run_command")
    def test_check_updates_uses_refresh_list(self, mock_run, mock_exists):
        mock_exists.return_value = True
        fake_refresh_list = (
            "Name        Version         Rev   Size    Publisher   Notes\n"
            "code        8a14f0cc        281   607MB   vscode      classic\n"
            "snap-store  0+git.d029eeda  1504  12.3MB  canonical   -\n"
        )
        mock_run.return_value = (0, fake_refresh_list, "")

        info = self.snap.check_updates()
        self.assertEqual(info["total"], 2)
        self.assertEqual(len(info["details"]), 2)
        self.assertIn("code", info["details"][0])


if __name__ == "__main__":
    unittest.main()
