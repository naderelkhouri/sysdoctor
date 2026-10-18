"""
Testes para a interface de monitoramento e dashboard em tempo real.
"""

import unittest
from rich.layout import Layout
from rich.table import Table
from sysdoctor.ui.dashboard import make_layout, get_top_processes, generate_dashboard_grid


class TestDashboard(unittest.TestCase):
    def test_make_layout(self):
        layout = make_layout()
        self.assertIsInstance(layout, Layout)
        self.assertTrue(hasattr(layout, "split"))

    def test_get_top_processes(self):
        table = get_top_processes(count=5)
        self.assertIsInstance(table, Table)
        self.assertEqual(len(table.columns), 4)

    def test_generate_dashboard_grid(self):
        grid = generate_dashboard_grid()
        self.assertIsInstance(grid, Layout)
        self.assertIsNotNone(grid.get("header"))
        self.assertIsNotNone(grid.get("main"))
        self.assertIsNotNone(grid.get("footer"))


if __name__ == "__main__":
    unittest.main()
