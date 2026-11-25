"""
Painel TUI Interativo em Tempo Real utilizando Rich Live.
"""

import time
import psutil
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.text import Text
from sysdoctor.core.system import collect_system_metrics
from sysdoctor.ui.theme import (
    CARD_BOX,
    TABLE_BOX,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_BORDER,
    COLOR_TEXT_DIM,
    render_gauge,
    format_bytes_human,
)
from sysdoctor import __version__


def make_layout() -> Layout:
    """Cria a estrutura de layout do Dashboard."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=4),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1),
    )
    return layout


_PROCESS_CACHE = {}


def get_top_processes(count: int = 8) -> Table:
    """Retorna tabela com os processos que mais consomem CPU e RAM."""
    global _PROCESS_CACHE
    table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
    table.add_column("PID", width=8, justify="right", style=COLOR_TEXT_DIM)
    table.add_column("Nome do Processo", ratio=1, style="bold")
    table.add_column("CPU %", width=10, justify="right")
    table.add_column("RAM %", width=10, justify="right")

    current_pids = set(psutil.pids())
    _PROCESS_CACHE = {pid: p for pid, p in _PROCESS_CACHE.items() if pid in current_pids}

    procs = []
    for pid in current_pids:
        p = _PROCESS_CACHE.get(pid)
        if p is None:
            try:
                p = psutil.Process(pid)
                p.cpu_percent()
                _PROCESS_CACHE[pid] = p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        try:
            procs.append({
                "pid": pid,
                "name": p.name(),
                "cpu_percent": p.cpu_percent(),
                "memory_percent": p.memory_percent(),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    has_cpu_signal = any((p["cpu_percent"] or 0) > 0 for p in procs)
    if has_cpu_signal:
        top_procs = sorted(procs, key=lambda x: x["cpu_percent"] or 0, reverse=True)[:count]
    else:
        top_procs = sorted(procs, key=lambda x: x["memory_percent"] or 0, reverse=True)[:count]

    for p in top_procs:
        cpu_val = p["cpu_percent"] or 0.0
        mem_val = p["memory_percent"] or 0.0

        cpu_color = COLOR_DANGER if cpu_val > 50 else (COLOR_WARNING if cpu_val > 20 else "white")
        mem_color = COLOR_DANGER if mem_val > 30 else (COLOR_WARNING if mem_val > 15 else "white")

        table.add_row(
            str(p["pid"]),
            (p["name"] or "desconhecido")[:20],
            f"[{cpu_color}]{cpu_val:5.1f}%[/{cpu_color}]",
            f"[{mem_color}]{mem_val:5.1f}%[/{mem_color}]",
        )

    return table


def generate_dashboard_grid() -> Layout:
    """Gera o painel completo atualizado para renderização no Live."""
    layout = make_layout()
    metrics = collect_system_metrics(lightweight=True)

    # Header
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=3)
    grid.add_column(justify="right", ratio=2)

    left_h = Text()
    left_h.append("🩺  SYSDOCTOR MONITOR", style=f"bold {COLOR_PRIMARY_LIGHT}")
    left_h.append(f"  v{__version__}\n", style=f"bold {COLOR_SECONDARY}")
    left_h.append(f"Host: {metrics.hostname} ({metrics.os_name})", style=f"dim {COLOR_TEXT_DIM}")

    right_h = Text(justify="right")
    right_h.append("● MONITORAMENTO AO VIVO\n", style=f"bold {COLOR_SUCCESS}")
    uptime_h = metrics.uptime_seconds / 3600.0
    hw = metrics.sensors
    temp_s = f" | {hw.max_temperature:.0f}°C" if hw and hw.max_temperature else ""
    right_h.append(f"Uptime: {uptime_h:.1f}h{temp_s}", style=f"dim {COLOR_TEXT_DIM}")

    grid.add_row(left_h, right_h)
    layout["header"].update(Panel(grid, border_style=COLOR_PRIMARY, box=CARD_BOX, padding=(0, 1)))

    # Left: Recursos Globais
    left_table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
    left_table.add_column("Recurso", width=14, style="bold")
    left_table.add_column("Uso Proporcional", ratio=1)

    left_table.add_row("CPU Global", render_gauge(metrics.cpu_percent, width=18))
    left_table.add_row("Memória RAM", render_gauge(metrics.memory_percent, width=18))
    left_table.add_row("Memória Swap", render_gauge(metrics.swap_percent, width=18))

    for disk in metrics.disks:
        left_table.add_row(f"Disco ({disk.mountpoint})", render_gauge(disk.percent, width=18))

    layout["left"].update(
        Panel(left_table, title=f"[bold {COLOR_PRIMARY_LIGHT}]📊 Recursos Físicos[/]", border_style=COLOR_BORDER, box=CARD_BOX)
    )

    # Right: Top Processos
    top_proc_table = get_top_processes(count=7)
    layout["right"].update(
        Panel(top_proc_table, title=f"[bold {COLOR_PRIMARY_LIGHT}]🔥 Top Processos Ativos[/]", border_style=COLOR_BORDER, box=CARD_BOX)
    )

    # Footer
    footer_text = Text("Pressione [Ctrl+C] ou [q] para retornar ao terminal.", style=COLOR_TEXT_DIM, justify="center")
    layout["footer"].update(Panel(footer_text, border_style=COLOR_BORDER, box=CARD_BOX))

    return layout


def start_live_dashboard(refresh_per_second: float = 1.0):
    """Inicia o loop do monitor de tempo real com detecção imediata de saída por 'q' ou Ctrl+C."""
    import select
    from sysdoctor.ui.selector import RawTerminal, is_interactive_tty

    console = Console()
    interval = 1.0 / max(0.2, refresh_per_second)

    if not is_interactive_tty():
        try:
            with Live(generate_dashboard_grid(), refresh_per_second=refresh_per_second, console=console) as live:
                while True:
                    time.sleep(interval)
                    live.update(generate_dashboard_grid())
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold green]Monitoramento encerrado.[/bold green]")
        return

    try:
        with RawTerminal() as term:
            with Live(generate_dashboard_grid(), refresh_per_second=refresh_per_second, console=console) as live:
                while True:
                    if term.fd is not None:
                        r, _, _ = select.select([term.fd], [], [], interval)
                        if r:
                            key = term.read_key()
                            if key in ("q", "Q", "ESC", "CTRL_C", "CTRL_D", "ENTER"):
                                break
                    else:
                        time.sleep(interval)

                    live.update(generate_dashboard_grid())
    except (KeyboardInterrupt, EOFError):
        pass

    console.print("\n[bold green]Monitoramento encerrado.[/bold green]")
