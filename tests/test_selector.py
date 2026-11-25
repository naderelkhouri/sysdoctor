"""
Testes para o módulo de seletores interativos com setas (sysdoctor.ui.selector).
"""

import unittest
from unittest.mock import patch
from rich.table import Table
from sysdoctor.ui.selector import (
    MenuItem,
    CheckboxItem,
    render_menu_table,
    render_checkbox_table,
    arrow_select_menu,
    arrow_checkbox_select,
    read_single_key,
    is_interactive_tty,
)


class TestSelector(unittest.TestCase):
    def setUp(self):
        self.menu_items = [
            MenuItem("1", "🩺 Relatório", "Exibe o relatório", "Normal"),
            MenuItem("2", "🔧 Manutenção", "Executa tarefas de limpeza", "Sudo"),
            MenuItem("0", "🚪 Sair", "Encerra o programa", "—"),
        ]
        self.checkbox_items = [
            CheckboxItem("1", "APT", "Pacotes APT", True),
            CheckboxItem("2", "Docker", "Containers órfãos", False),
        ]

    def test_render_menu_table(self):
        table = render_menu_table(self.menu_items, active_idx=1)
        self.assertIsInstance(table, Table)
        self.assertEqual(len(table.rows), 3)

    def test_render_checkbox_table(self):
        table = render_checkbox_table(self.checkbox_items, active_idx=0)
        self.assertIsInstance(table, Table)
        self.assertEqual(len(table.rows), 2)

    @patch("sysdoctor.ui.selector.is_interactive_tty", return_value=False)
    @patch("builtins.input", return_value="2")
    def test_arrow_select_menu_non_interactive(self, mock_input, mock_tty):
        chosen = arrow_select_menu(self.menu_items)
        self.assertEqual(chosen, "2")

    @patch("sysdoctor.ui.selector.is_interactive_tty", return_value=False)
    def test_arrow_checkbox_select_non_interactive(self, mock_tty):
        chosen = arrow_checkbox_select(self.checkbox_items)
        self.assertEqual(chosen, ["1"])

    @patch("sysdoctor.ui.selector.is_interactive_tty", return_value=False)
    @patch("sys.stdin.readline", return_value="ENTER\n")
    def test_read_single_key_non_interactive(self, mock_readline, mock_tty):
        key = read_single_key()
        self.assertEqual(key, "ENTER")

    def test_decode_terminal_bytes(self):
        from sysdoctor.ui.selector import decode_terminal_bytes
        self.assertEqual(decode_terminal_bytes(b"\x1b[A"), "UP")
        self.assertEqual(decode_terminal_bytes(b"\x1b[B"), "DOWN")
        self.assertEqual(decode_terminal_bytes(b"\x1b[C"), "RIGHT")
        self.assertEqual(decode_terminal_bytes(b"\x1b[D"), "LEFT")
        self.assertEqual(decode_terminal_bytes(b"\r"), "ENTER")
        self.assertEqual(decode_terminal_bytes(b" "), "SPACE")
        self.assertEqual(decode_terminal_bytes(b"\x1b"), "ESC")
        self.assertEqual(decode_terminal_bytes(b"q"), "q")

    @patch("sysdoctor.ui.selector.is_interactive_tty", return_value=False)
    @patch("sys.stdin.readline", return_value="\n")
    def test_wait_for_return_non_interactive(self, mock_readline, mock_tty):
        from sysdoctor.ui.selector import wait_for_return
        wait_for_return()  # should execute cleanly without raising


if __name__ == "__main__":
    unittest.main()
