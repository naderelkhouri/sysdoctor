"""
Testes para o módulo de inspeção de sistema.
"""

import unittest
from sysdoctor.core.system import (
    detect_linux_distro,
    collect_system_metrics,
    get_top_processes,
    collect_hardware_sensors,
    get_kernel_tuning_info,
    inspect_disk_hogs,
    SystemMetrics,
    HardwareSensors,
)


class TestSystemInspection(unittest.TestCase):
    def test_detect_linux_distro(self):
        distro = detect_linux_distro()
        self.assertIsInstance(distro, str)
        self.assertTrue(len(distro) > 0)

    def test_get_top_processes(self):
        top_cpu, top_mem, top_swap = get_top_processes(count=3)
        self.assertIsInstance(top_cpu, list)
        self.assertIsInstance(top_mem, list)
        self.assertIsInstance(top_swap, list)
        if top_mem:
            self.assertGreater(top_mem[0].pid, 0)
            self.assertTrue(len(top_mem[0].name) > 0)

    def test_collect_hardware_sensors(self):
        sensors = collect_hardware_sensors()
        self.assertIsInstance(sensors, HardwareSensors)
        self.assertIsInstance(sensors.temperatures, dict)
        self.assertGreaterEqual(sensors.max_temperature, 0.0)

    def test_get_kernel_tuning_info(self):
        zram_active, swappiness = get_kernel_tuning_info()
        self.assertIsInstance(zram_active, bool)
        if swappiness is not None:
            self.assertIsInstance(swappiness, int)

    def test_inspect_disk_hogs(self):
        hogs = inspect_disk_hogs()
        self.assertIsInstance(hogs, list)

    def test_collect_system_metrics(self):
        metrics = collect_system_metrics()
        self.assertIsInstance(metrics, SystemMetrics)
        self.assertTrue(0.0 <= metrics.cpu_percent <= 100.0)
        self.assertTrue(0.0 <= metrics.memory_percent <= 100.0)
        self.assertTrue(metrics.cpu_count_logical >= 1)
        self.assertTrue(len(metrics.hostname) > 0)
        self.assertIsInstance(metrics.top_cpu_processes, list)
        self.assertIsInstance(metrics.top_memory_processes, list)
        self.assertIsInstance(metrics.disk_hogs, list)

    def test_collect_system_metrics_lightweight(self):
        metrics = collect_system_metrics(lightweight=True)
        self.assertIsInstance(metrics, SystemMetrics)
        self.assertEqual(metrics.disk_hogs, [])
        self.assertEqual(metrics.top_cpu_processes, [])
        self.assertEqual(metrics.failed_systemd_units, [])


if __name__ == "__main__":
    unittest.main()
