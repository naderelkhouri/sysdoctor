"""
Testes para o gerenciador de pacotes APT e proteção contra remoção de bootloader.
"""

import unittest
from unittest.mock import patch
from sysdoctor.package_managers.apt import AptPackageManager


class TestAptPackageManager(unittest.TestCase):
    def setUp(self):
        self.apt = AptPackageManager()

    @patch("sysdoctor.package_managers.apt.command_exists")
    @patch("sysdoctor.package_managers.apt.run_command")
    def test_get_residual_packages(self, mock_run, mock_exists):
        mock_exists.return_value = True
        fake_dpkg_output = (
            "Desired=Unknown/Install/Remove/Purge/Status\n"
            "| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend\n"
            "|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)\n"
            "||/ Name           Version      Architecture Description\n"
            "+++-==============-============-============-=================================\n"
            "rc  grub-pc        2.12-1       amd64        GRand Unified Bootloader (PC)\n"
            "rc  old-lib-test   1.0.0        amd64        Old test library\n"
            "ii  nano           7.2-1        amd64        Small, friendly text editor\n"
            "rc  linux-image-old 6.2.0-1     amd64        Linux kernel image\n"
        )
        mock_run.return_value = (0, fake_dpkg_output, "")

        residuals = self.apt.get_residual_packages()
        self.assertEqual(residuals, ["grub-pc", "old-lib-test", "linux-image-old"])

    @patch("sysdoctor.package_managers.apt.command_exists")
    @patch("sysdoctor.package_managers.apt.run_command")
    def test_clean_residual_packages_protects_grub_and_kernel(self, mock_run, mock_exists):
        mock_exists.return_value = True
        fake_dpkg_output = (
            "rc  grub-pc           2.12-1   amd64  GRUB PC\n"
            "rc  shim-signed       1.50     amd64  Shim bootloader\n"
            "rc  old-unused-app    1.0      amd64  Unused app\n"
            "rc  linux-image-6.1   6.1      amd64  Kernel image\n"
        )
        # First call is dpkg -l, second is dpkg --purge
        mock_run.side_effect = [
            (0, fake_dpkg_output, ""),
            (0, "Purged successfully", ""),
        ]

        succ, msg = self.apt.clean_residual_packages(dry_run=False)
        self.assertTrue(succ)
        self.assertIn("1 pacotes residuais limpos com segurança", msg)
        self.assertIn("3 pacotes críticos de boot/kernel protegidos", msg)

        # Verifica se o comando executado incluiu APENAS 'old-unused-app' e NUNCA 'grub-pc', 'shim-signed' ou 'linux-image-6.1'
        second_call_cmd = mock_run.call_args_list[1][0][0]
        self.assertIn("dpkg", second_call_cmd)
        self.assertIn("--purge", second_call_cmd)
        self.assertIn("old-unused-app", second_call_cmd)
        self.assertNotIn("grub-pc", second_call_cmd)
        self.assertNotIn("shim-signed", second_call_cmd)
        self.assertNotIn("linux-image-6.1", second_call_cmd)


if __name__ == "__main__":
    unittest.main()
