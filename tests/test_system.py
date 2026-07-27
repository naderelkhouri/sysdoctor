"""
Testes para o módulo de inspeção de sistema.
"""

import unittest
from sysdoctor.core.system import (
    detect_linux_distro,
    collect_system_metrics,
    SystemMetrics,
)


class TestSystemInspection(unittest.TestCase):
    def test_detect_linux_distro(self):
        distro = detect_linux_distro()
        self.assertIsInstance(distro, str)
        self.assertTrue(len(distro) > 0)

    def test_collect_system_metrics(self):
        metrics = collect_system_metrics()
        self.assertIsInstance(metrics, SystemMetrics)
        self.assertTrue(0.0 <= metrics.cpu_percent <= 100.0)
        self.assertTrue(0.0 <= metrics.memory_percent <= 100.0)
        self.assertTrue(metrics.cpu_count_logical >= 1)
        self.assertTrue(len(metrics.hostname) > 0)


if __name__ == "__main__":
    unittest.main()
