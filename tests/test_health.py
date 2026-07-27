"""
Testes para o cálculo de pontuação de saúde (Health Score).
"""

import unittest
from sysdoctor.core.system import SystemMetrics
from sysdoctor.core.health import evaluate_health


class TestHealthAssessment(unittest.TestCase):
    def test_health_evaluation_healthy_system(self):
        metrics = SystemMetrics(
            os_name="Linux Mint 21",
            kernel_version="6.5.0-generic",
            architecture="x86_64",
            hostname="test-host",
            uptime_seconds=3600.0,
            cpu_percent=15.0,
            cpu_count_logical=8,
            cpu_count_physical=4,
            memory_percent=30.0,
            memory_total_bytes=16000000000,
            memory_used_bytes=4800000000,
            memory_available_bytes=11200000000,
            swap_percent=0.0,
            swap_total_bytes=8000000000,
            swap_used_bytes=0,
            disks=[],
            failed_systemd_units=[],
            reboot_required=False,
        )
        pkg_summary = {"total": 0, "security": 0, "phased": False, "managers": {}}

        assessment = evaluate_health(metrics, pkg_summary)
        self.assertEqual(assessment.score, 100)
        self.assertEqual(assessment.status_label, "Excelente")
        self.assertEqual(assessment.status_color, "green")

    def test_health_evaluation_critical_system(self):
        metrics = SystemMetrics(
            os_name="Ubuntu 22.04",
            kernel_version="5.15.0-generic",
            architecture="x86_64",
            hostname="test-host",
            uptime_seconds=3600.0,
            cpu_percent=95.0,
            cpu_count_logical=8,
            cpu_count_physical=4,
            memory_percent=95.0,
            memory_total_bytes=16000000000,
            memory_used_bytes=15200000000,
            memory_available_bytes=800000000,
            swap_percent=80.0,
            swap_total_bytes=8000000000,
            swap_used_bytes=6400000000,
            disks=[],
            failed_systemd_units=["nginx.service"],
            reboot_required=True,
        )
        pkg_summary = {"total": 10, "security": 3, "phased": False, "managers": {}}

        assessment = evaluate_health(metrics, pkg_summary)
        self.assertLess(assessment.score, 50)
        self.assertEqual(assessment.status_label, "Crítico")
        self.assertEqual(assessment.status_color, "red")
        self.assertGreaterEqual(len(assessment.items), 4)


if __name__ == "__main__":
    unittest.main()
