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


if __name__ == "__main__":
    unittest.main()
