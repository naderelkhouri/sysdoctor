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
from sysdoctor.ui.views import make_progress_bar
from sysdoctor import __version__


def make_layout() -> Layout:
    """Cria a estrutura de layout do Dashboard."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1),
    )
    return layout


def get_top_processes(count: int = 8) -> Table:
    """Retorna tabela com os processos que mais consomem CPU e RAM."""
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("PID", width=7)
    table.add_column("Nome", width=18)
    table.add_column("CPU %", width=8)
    table.add_column("RAM %", width=8)

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Ordena por CPU %
    top_cpu = sorted(procs, key=lambda x: x["cpu_percent"] or 0, reverse=True)[:count]

    for p in top_cpu:
        table.add_row(
            str(p["pid"]),
            (p["name"] or "desconhecido")[:17],
            f"{p['cpu_percent'] or 0:.1f}",
            f"{p['memory_percent'] or 0:.1f}",
        )

    return table


def generate_dashboard_grid() -> Layout:
    """Gera o painel completo atualizado para renderização no Live."""
    layout = make_layout()
    metrics = collect_system_metrics()

    # Header
    header_text = Text()
    header_text.append("🩺 SysDoctor Monitor ", style="bold cyan")
    header_text.append(f"v{__version__} | ", style="dim white")
    header_text.append(f"Host: {metrics.hostname} ({metrics.os_name})", style="bold white")
    layout["header"].update(Panel(header_text, border_style="cyan"))

    # Left: Métricas principais
    left_table = Table(show_header=False, box=None, padding=(0, 1))
    left_table.add_column("Item", width=12)
    left_table.add_column("Barra", width=30)

    left_table.add_row("CPU Global", make_progress_bar(metrics.cpu_percent))
    left_table.add_row("RAM Usada", make_progress_bar(metrics.memory_percent))
    left_table.add_row("Swap Usado", make_progress_bar(metrics.swap_percent))

    for disk in metrics.disks:
        left_table.add_row(f"Disco {disk['mountpoint']}", make_progress_bar(disk["percent"]))

    layout["left"].update(Panel(left_table, title="[bold]📊 Recursos em Tempo Real[/bold]", border_style="green"))

    # Right: Processos do Sistema
    top_proc_table = get_top_processes()
    layout["right"].update(Panel(top_proc_table, title="[bold]🔥 Top Processos (CPU/RAM)[/bold]", border_style="yellow"))

    # Footer
    footer_text = Text("Pressione Ctrl+C para sair do monitoramento em tempo real.", style="dim white", justify="center")
    layout["footer"].update(Panel(footer_text, border_style="dim"))

    return layout


def start_live_dashboard(refresh_per_second: float = 1.0):
    """Inicia o loop do monitor de tempo real."""
    console = Console()
    try:
        with Live(generate_dashboard_grid(), refresh_per_second=refresh_per_second, console=console) as live:
            while True:
                time.sleep(1.0 / refresh_per_second)
                live.update(generate_dashboard_grid())
    except KeyboardInterrupt:
        console.print("\n[bold green]Monitoramento encerrado.[/bold green]")
