"""
Visões e componentes de interface Rich para relatórios.
"""

from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns
from rich.text import Text
from sysdoctor.ui.theme import console
from sysdoctor import __version__


def make_progress_bar(percent: float, width: int = 25) -> str:
    """Retorna uma barra textual colorida de porcentagem."""
    filled = int(width * percent / 100)
    empty = width - filled

    if percent < 70:
        color = "green"
    elif percent < 85:
        color = "yellow"
    else:
        color = "red"

    bar_str = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim] [{color}]{percent:5.1f}%[/{color}]"
    return bar_str


def print_banner():
    """Imprime o cabeçalho do SysDoctor."""
    banner_text = Text()
    banner_text.append("🩺 SysDoctor", style="bold cyan")
    banner_text.append(f" v{__version__}", style="dim white")
    banner_text.append(" — Diagnóstico & Manutenção Linux\n", style="bold white")
    console.print(Panel(banner_text, border_style="cyan", expand=False))


def display_report(report_data: Dict[str, Any]):
    """Renderiza um relatório completo e bonito utilizando Rich."""
    print_banner()

    sys_info = report_data["system"]
    health = report_data["health"]
    packages = report_data["packages"]

    # 1. Painel de Informações do Sistema
    sys_table = Table(show_header=False, box=None, padding=(0, 1))
    sys_table.add_column("Chave", style="bold cyan")
    sys_table.add_column("Valor", style="white")

    sys_table.add_row("SO", sys_info["os_name"])
    sys_table.add_row("Kernel", sys_info["kernel"])
    sys_table.add_row("Hostname", sys_info["hostname"])

    uptime_hours = sys_info["uptime_seconds"] / 3600
    sys_table.add_row("Uptime", f"{uptime_hours:.1f} horas")

    console.print(Panel(sys_table, title="[bold]💻 Informações do Sistema[/bold]", border_style="blue"))

    # 2. Painel de Recursos (CPU, RAM, Discos)
    res_table = Table(show_header=True, header_style="bold cyan", box=None)
    res_table.add_column("Recurso", width=15)
    res_table.add_column("Uso / Capacidade", width=35)

    res_table.add_row("CPU", make_progress_bar(sys_info["cpu_percent"]))
    res_table.add_row("Memória RAM", make_progress_bar(sys_info["memory_percent"]))
    res_table.add_row("Swap", make_progress_bar(sys_info["swap_percent"]))

    for disk in sys_info["disks"]:
        res_table.add_row(f"Disco ({disk['mountpoint']})", make_progress_bar(disk["percent"]))

    console.print(Panel(res_table, title="[bold]📊 Recursos do Sistema[/bold]", border_style="cyan"))

    # 3. Painel de Pacotes e Atualizações
    pkg_table = Table(show_header=True, header_style="bold cyan", box=None)
    pkg_table.add_column("Gerenciador", width=25)
    pkg_table.add_column("Atualizações Pendentes", width=25)
    pkg_table.add_column("Segurança", width=15)

    for mgr_name, mgr_info in packages.get("managers", {}).items():
        tot = mgr_info.get("total", 0)
        sec = mgr_info.get("security", 0)
        tot_str = f"[yellow]{tot}[/yellow]" if tot > 0 else "[green]OK[/green]"
        sec_str = f"[bold red]{sec}[/bold red]" if sec > 0 else "[green]OK[/green]"
        pkg_table.add_row(mgr_name, tot_str, sec_str)

    console.print(Panel(pkg_table, title="[bold]📦 Pacotes e Atualizações[/bold]", border_style="magenta"))

    # 4. Health Score Card
    score = health["score"]
    color = health["status_color"]
    label = health["status_label"]

    score_panel = Panel(
        AlignTextCentral(f"[{color}][bold size=24]{score}/100[/bold size=24]\nStatus: {label}[/{color}]"),
        title="[bold]🩺 Health Score[/bold]",
        border_style=color,
    )
    console.print(score_panel)

    # 5. Recomendações e Diagnósticos
    if health["items"]:
        diag_table = Table(show_header=True, header_style="bold yellow", box=None)
        diag_table.add_column("Severidade", width=12)
        diag_table.add_column("Categoria", width=12)
        diag_table.add_column("Problema", width=25)
        diag_table.add_column("Sugestão de Ação", width=30)

        for item in health["items"]:
            sev_color = "red" if item["severity"] == "CRITICAL" else "yellow"
            diag_table.add_row(
                f"[{sev_color}]{item['severity']}[/{sev_color}]",
                item["category"],
                item["title"],
                item["action"],
            )

        console.print(Panel(diag_table, title="[bold]⚠️ Diagnósticos e Alertas[/bold]", border_style="yellow"))

    # Ações recomendadas
    console.print("\n[bold cyan]📌 Ações Recomendadas:[/bold cyan]")
    for act in health["recommended_actions"]:
        console.print(f"  • {act}")
    console.print()


class AlignTextCentral:
    def __init__(self, text: str):
        self.text = text

    def __rich__(self):
        return Text.from_markup(self.text, justify="center")
