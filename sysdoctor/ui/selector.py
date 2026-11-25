"""
Seletores interativos com navegação por setas (↑/↓), atalhos e suporte a checkboxes.
Totalmente autônomo, sem dependências externas (utiliza /dev/tty e termios/tty padrão).
Suporta execução sob sudo, tmux, scripts de inicialização e terminais virtuais.
"""

import sys
import os
import select
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from rich.panel import Panel
from rich.table import Table
from rich import box

from sysdoctor.ui.theme import (
    console,
    CARD_BOX,
    TABLE_BOX,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)


@dataclass
class MenuItem:
    key: str
    label: str
    desc: str
    access: str = "Normal"


@dataclass
class CheckboxItem:
    id: str
    label: str
    desc: str
    checked: bool = False


ESCAPE_SEQUENCES = {
    b"\x1b[A": "UP",
    b"\x1b[B": "DOWN",
    b"\x1b[C": "RIGHT",
    b"\x1b[D": "LEFT",
    b"\x1bOA": "UP",
    b"\x1bOB": "DOWN",
    b"\x1bOC": "RIGHT",
    b"\x1bOD": "LEFT",
    b"\x1b[H": "HOME",
    b"\x1b[F": "END",
}


def get_controlling_terminal() -> Tuple[Optional[Any], Optional[int]]:
    """
    Obtém uma conexão direta com o terminal de entrada.
    Prioriza sys.stdin se for um tty interativo; caso contrário tenta /dev/tty.
    """
    # 1. Prioriza sys.stdin se for um TTY interativo
    try:
        if sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
            return None, sys.stdin.fileno()
    except Exception:
        pass

    # 2. Descritor 0 (stdin padrão POSIX)
    try:
        if os.isatty(0):
            return None, 0
    except Exception:
        pass

    # 3. Tenta /dev/tty apenas se stdin foi redirecionado mas há terminal controlador
    try:
        f = open("/dev/tty", "rb", buffering=0)
        fd = f.fileno()
        if os.isatty(fd):
            return f, fd
        f.close()
    except Exception:
        pass

    return None, None


def is_interactive_tty() -> bool:
    """Verifica se há um terminal interativo real disponível."""
    try:
        if sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
            return True
        if os.isatty(0):
            return True
    except Exception:
        pass

    f, fd = get_controlling_terminal()
    if f:
        try:
            f.close()
        except Exception:
            pass
    return fd is not None


def decode_terminal_bytes(raw: bytes) -> str:
    """Decodifica sequência de bytes recebidos do terminal."""
    if not raw:
        return ""
    if raw in ESCAPE_SEQUENCES:
        return ESCAPE_SEQUENCES[raw]
    if raw in (b"\r", b"\n"):
        return "ENTER"
    if raw == b" ":
        return "SPACE"
    if raw == b"\x03":  # Ctrl+C
        return "CTRL_C"
    if raw == b"\x04":  # Ctrl+D
        return "CTRL_D"
    if raw == b"\x1b":  # ESC isolado
        return "ESC"

    # Sequências ANSI compostas
    if raw.startswith(b"\x1b"):
        if b"A" in raw:
            return "UP"
        if b"B" in raw:
            return "DOWN"
        if b"C" in raw:
            return "RIGHT"
        if b"D" in raw:
            return "LEFT"
        return "ESC"

    try:
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""


class RawTerminal:
    """Gerenciador de contexto para leitura direta e sem eco do teclado."""

    def __init__(self):
        self._file_obj, self.fd = get_controlling_terminal()
        self.old_settings = None

    def __enter__(self):
        if self.fd is not None:
            try:
                import termios
                import tty

                self.old_settings = termios.tcgetattr(self.fd)
                tty.setcbreak(self.fd)
                # Oculta o cursor piscante
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd is not None:
            try:
                # Restaura o cursor
                sys.stdout.write("\033[?25h")
                sys.stdout.flush()
                if self.old_settings is not None:
                    import termios

                    termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass

        if self._file_obj:
            try:
                self._file_obj.close()
            except Exception:
                pass

    def read_key(self) -> str:
        """Lê tecla com detecção precisa de sequências de escape."""
        if self.fd is None:
            try:
                line = sys.stdin.readline()
                return line.strip() if line else "ENTER"
            except Exception:
                return "0"

        try:
            b = os.read(self.fd, 32)
            if not b:
                return ""

            if b == b"\x1b" or (b.startswith(b"\x1b") and len(b) <= 2):
                r, _, _ = select.select([self.fd], [], [], 0.05)
                if r:
                    more = os.read(self.fd, 32)
                    b += more

            return decode_terminal_bytes(b)
        except Exception:
            return ""


def read_single_key() -> str:
    """Função utilitária avulsa de leitura de tecla."""
    if not is_interactive_tty():
        try:
            line = sys.stdin.readline()
            return line.strip() if line else "ENTER"
        except Exception:
            return "ENTER"

    with RawTerminal() as term:
        return term.read_key()


def wait_for_return():
    """Aguarda o usuário pressionar Enter ou qualquer tecla sem vazar caracteres."""
    if not is_interactive_tty():
        return

    console.print(f"\n[{COLOR_TEXT_DIM}]Pressione [bold green]Enter[/] ou qualquer tecla para continuar...[/]")
    with RawTerminal() as term:
        term.read_key()


def render_menu_table(items: List[MenuItem], active_idx: int) -> Table:
    """Gera tabela estilizada para o seletor com linha ativa destacada."""
    table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
    table.add_column(" ", width=3, justify="center")
    table.add_column("Opção", width=7, justify="center")
    table.add_column("Módulo de Ação", width=28)
    table.add_column("Descrição Funcional", ratio=1)
    table.add_column("Acesso", width=10, justify="center")

    for idx, item in enumerate(items):
        is_sel = idx == active_idx
        cursor = f"[bold {COLOR_PRIMARY_LIGHT}]❯[/]" if is_sel else " "
        key_styled = f"[bold {COLOR_PRIMARY_LIGHT}][{item.key}][/]" if not is_sel else f"[bold white on {COLOR_PRIMARY}] {item.key} [/]"

        if is_sel:
            lbl = f"[bold {COLOR_PRIMARY_LIGHT}]{item.label}[/]"
            desc = f"[bold white]{item.desc}[/]"
        else:
            lbl = f"[white]{item.label}[/]"
            desc = f"[{COLOR_TEXT_DIM}]{item.desc}[/]"

        acc_str = f"[bold {COLOR_WARNING}]Sudo[/]" if item.access.lower() == "sudo" else f"[bold green]{item.access}[/]"

        table.add_row(cursor, key_styled, lbl, desc, acc_str)

    return table


def arrow_select_menu(
    items: List[MenuItem],
    title: str = "CENTRAL DE OPERAÇÕES DO SISTEMA",
    subtitle: str = "Navegue com [↑/↓] e confirme com [Enter]",
    default_idx: int = 0,
) -> str:
    """
    Exibe um seletor interativo navegável por setas direcionais.
    Permite também seleção direta digitando a tecla de atalho.
    """
    if not is_interactive_tty():
        console.print(f"\n[bold]{title}[/bold]")
        for item in items:
            console.print(f" [{item.key}] {item.label} - {item.desc}")
        try:
            choice = input("\nsysdoctor ❯ ").strip()
            return choice if choice else items[0].key
        except (KeyboardInterrupt, EOFError):
            return "0"

    from sysdoctor.ui.views import print_banner

    active_idx = max(0, min(len(items) - 1, default_idx))

    def make_panel(idx: int) -> Panel:
        tbl = render_menu_table(items, idx)
        nav_hints = (
            f"[{COLOR_TEXT_DIM}]Navegar:[/] [bold {COLOR_PRIMARY_LIGHT}]↑/↓[/] ou [bold {COLOR_PRIMARY_LIGHT}]j/k[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Confirmar:[/] [bold green]Enter[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Atalho:[/] [bold]0-9[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Sair:[/] [bold {COLOR_DANGER}]q[/]"
        )
        return Panel(
            tbl,
            title=f"[bold {COLOR_PRIMARY_LIGHT}]⚡ {title}[/]",
            subtitle=nav_hints,
            border_style=COLOR_BORDER_FOCUS,
            box=CARD_BOX,
            padding=(0, 1),
        )

    with RawTerminal() as term:
        while True:
            console.clear()
            print_banner(subtitle="Central Interativa de Manutenção e Diagnóstico")
            console.print(make_panel(active_idx))

            key = term.read_key()
            if not key:
                continue

            if key in ("UP", "k", "K"):
                active_idx = (active_idx - 1) % len(items)
            elif key in ("DOWN", "j", "J"):
                active_idx = (active_idx + 1) % len(items)
            elif key == "ENTER":
                return items[active_idx].key
            elif key in ("q", "Q", "ESC", "CTRL_C", "CTRL_D"):
                return "0"
            else:
                for it in items:
                    if key.lower() == it.key.lower():
                        return it.key


def render_checkbox_table(items: List[CheckboxItem], active_idx: int) -> Table:
    """Gera tabela com caixas de seleção interativas (checkboxes)."""
    table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
    table.add_column(" ", width=3, justify="center")
    table.add_column("Estado", width=8, justify="center")
    table.add_column("Componente / Módulo", width=34)
    table.add_column("Detalhe", ratio=1)

    for idx, item in enumerate(items):
        is_cursor = idx == active_idx
        cursor = f"[bold {COLOR_PRIMARY_LIGHT}]❯[/]" if is_cursor else " "

        if item.checked:
            state_box = f"[bold {COLOR_SUCCESS}]☑ SIM[/]"
        else:
            state_box = f"[{COLOR_TEXT_DIM}]☐ NÃO[/]"

        if is_cursor:
            lbl = f"[bold {COLOR_PRIMARY_LIGHT}]{item.label}[/]"
            desc = f"[bold white]{item.desc}[/]"
        else:
            lbl = f"[white]{item.label}[/]"
            desc = f"[{COLOR_TEXT_DIM}]{item.desc}[/]"

        table.add_row(cursor, state_box, lbl, desc)

    return table


def arrow_checkbox_select(
    items: List[CheckboxItem],
    title: str = "SELEÇÃO GRANULAR DE MANUTENÇÃO",
) -> List[str]:
    """
    Exibe seletor múltiplo com checkboxes navegável por setas.
    [Espaço] marca/desmarca, [a] marca todos, [n] desmarca todos, [Enter] confirma.
    """
    if not is_interactive_tty():
        return [it.id for it in items if it.checked]

    active_idx = 0

    def make_panel(idx: int) -> Panel:
        tbl = render_checkbox_table(items, idx)
        nav_hints = (
            f"[{COLOR_TEXT_DIM}]Mover:[/] [bold {COLOR_PRIMARY_LIGHT}]↑/↓[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Alternar:[/] [bold]Espaço[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Todos:[/] [bold]a[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Executar:[/] [bold green]Enter[/]  "
            f"[{COLOR_BORDER}]│[/]  [{COLOR_TEXT_DIM}]Cancelar:[/] [bold {COLOR_DANGER}]q[/]"
        )
        return Panel(
            tbl,
            title=f"[bold {COLOR_PRIMARY_LIGHT}]🎯 {title}[/]",
            subtitle=nav_hints,
            border_style=COLOR_BORDER_FOCUS,
            box=CARD_BOX,
            padding=(0, 1),
        )

    with RawTerminal() as term:
        while True:
            console.clear()
            console.print(make_panel(active_idx))

            key = term.read_key()
            if not key:
                continue

            if key in ("UP", "k", "K"):
                active_idx = (active_idx - 1) % len(items)
            elif key in ("DOWN", "j", "J"):
                active_idx = (active_idx + 1) % len(items)
            elif key == "SPACE":
                items[active_idx].checked = not items[active_idx].checked
            elif key in ("a", "A"):
                for it in items:
                    it.checked = True
            elif key in ("n", "N"):
                for it in items:
                    it.checked = False
            elif key == "ENTER":
                return [it.id for it in items if it.checked]
            elif key in ("q", "Q", "ESC", "CTRL_C", "CTRL_D"):
                return []
