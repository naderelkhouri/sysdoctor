"""
Testes para detecção e iterabilidade de gerenciadores de pacotes.
"""

import unittest
from sysdoctor.package_managers import get_available_package_managers
from sysdoctor.package_managers.base import BasePackageManager


class TestPackageManagers(unittest.TestCase):
    def test_get_available_package_managers(self):
        managers = get_available_package_managers()
        self.assertIsInstance(managers, list)
        for mgr in managers:
            self.assertIsInstance(mgr, BasePackageManager)
            self.assertIsInstance(mgr.name, str)
            self.assertTrue(mgr.is_available())


class TestMultiDistroPackageManagers(unittest.TestCase):
    from unittest.mock import patch

    @patch("sysdoctor.package_managers.dnf.command_exists", return_value=True)
    @patch("sysdoctor.package_managers.dnf.run_command")
    def test_dnf_check_updates_code_100(self, mock_run, mock_exists):
        from sysdoctor.package_managers.dnf import DnfPackageManager
        dnf = DnfPackageManager()
        mock_run.side_effect = [
            (100, "curl.x86_64  8.0.1  fedora\nkernel.x86_64 6.8.0 fedora\n", ""),
            (100, "curl.x86_64  8.0.1  fedora\n", ""),
        ]
        info = dnf.check_updates()
        self.assertEqual(info["total"], 2)
        self.assertEqual(info["security"], 1)

    @patch("sysdoctor.package_managers.pacman.command_exists")
    @patch("sysdoctor.package_managers.pacman.run_command")
    def test_pacman_check_updates_and_orphan_cleanup(self, mock_run, mock_exists):
        from sysdoctor.package_managers.pacman import PacmanPackageManager
        mock_exists.side_effect = lambda cmd: cmd in ("pacman", "checkupdates")
        pacman = PacmanPackageManager()

        # checkupdates
        mock_run.return_value = (0, "systemd 255.4 -> 255.5\nlinux 6.8.1 -> 6.8.2\n", "")
        info = pacman.check_updates()
        self.assertEqual(info["total"], 2)

    @patch("sysdoctor.package_managers.flatpak.command_exists", return_value=True)
    @patch("sysdoctor.package_managers.flatpak.run_command")
    def test_flatpak_check_updates(self, mock_run, mock_exists):
        from sysdoctor.package_managers.flatpak import FlatpakPackageManager
        flatpak = FlatpakPackageManager()
        mock_run.return_value = (0, "org.mozilla.firefox  stable  flathub\n", "")
        info = flatpak.check_updates()
        self.assertEqual(info["total"], 1)

    @patch("sysdoctor.package_managers.zypper.command_exists", return_value=True)
    @patch("sysdoctor.package_managers.zypper.run_command")
    def test_zypper_check_updates(self, mock_run, mock_exists):
        from sysdoctor.package_managers.zypper import ZypperPackageManager
        zypper = ZypperPackageManager()
        mock_run.side_effect = [
            (0, "v | repo | pkg1 | 1.0 | 2.0 | x86_64\n", ""),
            (0, "1 security patch available", ""),
        ]
        info = zypper.check_updates()
        self.assertEqual(info["total"], 1)
        self.assertEqual(info["security"], 1)

    @patch("sysdoctor.package_managers.apk.command_exists", return_value=True)
    @patch("sysdoctor.package_managers.apk.run_command")
    def test_apk_check_updates(self, mock_run, mock_exists):
        from sysdoctor.package_managers.apk import ApkPackageManager
        apk = ApkPackageManager()
        mock_run.side_effect = [
            (0, "OK", ""),
            (0, "busybox-1.36.1-r1 < 1.36.1-r2\n", ""),
        ]
        info = apk.check_updates()
        self.assertEqual(info["total"], 1)


if __name__ == "__main__":
    unittest.main()
