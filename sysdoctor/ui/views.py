"""
Visões e componentes de interface Rich para relatórios do SysDoctor.
"""

from typing import Dict, Any, List
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import box

from sysdoctor import __version__
from sysdoctor.ui.theme import (
    console,
    CARD_BOX,
    TABLE_BOX,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_SECONDARY,
    COLOR_PURPLE,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_MUTED,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    make_badge,
    render_gauge,
    format_bytes_human,
)


def make_progress_bar(percent: float, width: int = 22) -> str:
    """Wrapper compatível que retorna barra de progresso estilizada."""
    return render_gauge(percent, width=width, show_badge=True)


def print_banner(subtitle: str = "Diagnóstico, Monitoramento & Manutenção Linux"):
    """Renderiza cabeçalho moderno e minimalista do SysDoctor."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=3)
    grid.add_column(justify="right", ratio=2)

    left_text = Text()
    left_text.append("🩺  SYSDOCTOR", style=f"bold {COLOR_PRIMARY_LIGHT}")
    left_text.append(f"  v{__version__}\n", style=f"bold {COLOR_SECONDARY}")
    left_text.append(f"◈  {subtitle}", style=f"dim {COLOR_TEXT_DIM}")

    right_text = Text(justify="right")
    right_text.append("● ENGINE PRONTA\n", style=f"bold {COLOR_SUCCESS}")
    right_text.append("Proteção & Desempenho Ativos", style=f"dim {COLOR_TEXT_DIM}")

    grid.add_row(left_text, right_text)

    banner_panel = Panel(
        grid,
        border_style=COLOR_PRIMARY,
        box=CARD_BOX,
        padding=(0, 2),
    )
    console.print(banner_panel)


def display_report(report_data: Dict[str, Any]):
    """Renderiza relatório visual completo de alto padrão."""
    print_banner()

    sys_info = report_data["system"]
    health = report_data["health"]
    packages = report_data["packages"]
    hw = sys_info.get("hardware", {})
    tuning = sys_info.get("tuning", {})

    # ─────────────────────────────────────────────────────────────────
    # 1. Painel Hero: Health Score Card
    # ─────────────────────────────────────────────────────────────────
    score = health["score"]
    label = health["status_label"].upper()

    if score >= 90:
        score_color = COLOR_SUCCESS
        badge_level = "SUCCESS"
    elif score >= 70:
        score_color = COLOR_SUCCESS
        badge_level = "SUCCESS"
    elif score >= 50:
        score_color = COLOR_WARNING
        badge_level = "WARNING"
    else:
        score_color = COLOR_DANGER
        badge_level = "CRITICAL"

    hero_grid = Table.grid(expand=True)
    hero_grid.add_column(justify="center")

    hero_grid.add_row(Align.center(make_badge(f"STATUS DO SISTEMA: {label}", level=badge_level)))
    hero_grid.add_row(
        Align.center(
            f"[bold {score_color} size=26]{score}[/bold {score_color} size=26]"
            f"[dim {COLOR_TEXT_DIM} size=18]/100[/dim {COLOR_TEXT_DIM} size=18]"
        )
    )
    hero_grid.add_row(Align.center(render_gauge(score, width=28, show_badge=False)))

    # Linha de Vitals Rápidos
    cpu_val = sys_info.get("cpu_percent", 0.0)
    ram_val = sys_info.get("memory_percent", 0.0)
    swap_val = sys_info.get("swap_percent", 0.0)
    temp_val = hw.get("max_temperature")

    vitals_parts = [
        f"[{COLOR_TEXT_DIM}]CPU:[/] [bold]{cpu_val:.1f}%[/]",
        f"[{COLOR_TEXT_DIM}]RAM:[/] [bold]{ram_val:.1f}%[/]",
        f"[{COLOR_TEXT_DIM}]Swap:[/] [bold]{swap_val:.1f}%[/]",
    ]
    if temp_val:
        vitals_parts.append(f"[{COLOR_TEXT_DIM}]Temp:[/] [bold]{temp_val:.1f}°C[/]")

    hero_grid.add_row(Align.center(f"  [{COLOR_BORDER}]│[/]  ".join(vitals_parts)))

    hero_panel = Panel(
        hero_grid,
        title=f"[bold {COLOR_PRIMARY_LIGHT}]🩺 ÍNDICE GLOBAL DE SAÚDE (HEALTH SCORE)[/]",
        subtitle=f"[{COLOR_TEXT_DIM}]Baseado em métricas de hardware, serviços e pacotes[/]",
        border_style=score_color,
        box=CARD_BOX,
        padding=(1, 2),
    )
    console.print(hero_panel)

    # ─────────────────────────────────────────────────────────────────
    # 2. Informações da Máquina & Hardware (Grade 2 Colunas)
    # ─────────────────────────────────────────────────────────────────
    info_table = Table(box=CARD_BOX, expand=True, border_style=COLOR_BORDER)
    info_table.add_column("💻 Plataforma & Sistema", style=COLOR_TEXT, ratio=1)
    info_table.add_column("⚡ Hardware & Otimizações", style=COLOR_TEXT, ratio=1)

    uptime_hours = sys_info["uptime_seconds"] / 3600.0
    col1 = (
        f"[{COLOR_PRIMARY_LIGHT}]Distribuição:[/] {sys_info['os_name']}\n"
        f"[{COLOR_PRIMARY_LIGHT}]Kernel:[/] {sys_info['kernel']} ({sys_info['architecture']})\n"
        f"[{COLOR_PRIMARY_LIGHT}]Hostname:[/] {sys_info['hostname']}\n"
        f"[{COLOR_PRIMARY_LIGHT}]Tempo Ativo:[/] {uptime_hours:.1f} horas"
    )

    temp_str = f"{hw['max_temperature']:.1f} °C" if hw.get("max_temperature") else "Indisponível"
    bat_str = f"{hw['battery_percent']:.0f}%" if hw.get("battery_percent") is not None else "N/A"
    if hw.get("battery_plugged"):
        bat_str += " (Tomada AC)"

    zram_badge = "[bold green]Ativo[/]" if tuning.get("zram_active") else "[dim]Inativo[/]"
    swp_val = tuning.get("swappiness", "N/A")

    col2 = (
        f"[{COLOR_PRIMARY_LIGHT}]Temperatura Máx.:[/] {temp_str}\n"
        f"[{COLOR_PRIMARY_LIGHT}]Bateria / Alimentação:[/] {bat_str}\n"
        f"[{COLOR_PRIMARY_LIGHT}]Compressão ZRAM:[/] {zram_badge}\n"
        f"[{COLOR_PRIMARY_LIGHT}]Parâmetro Swappiness:[/] {swp_val}"
    )

    info_table.add_row(col1, col2)
    console.print(info_table)

    # ─────────────────────────────────────────────────────────────────
    # 3. Painel de Recursos (CPU, Memória, Swap, Discos)
    # ─────────────────────────────────────────────────────────────────
    res_table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
    res_table.add_column("Recurso", width=18, style="bold")
    res_table.add_column("Uso Proporcional", width=34)
    res_table.add_column("Capacidade / Detalhe", justify="right", style=COLOR_TEXT_DIM)

    # Memória formatada
    mem_total_str = format_bytes_human(sys_info.get("memory_total_bytes", 0))
    mem_used_str = format_bytes_human(sys_info.get("memory_used_bytes", 0))
    swap_total_str = format_bytes_human(sys_info.get("swap_total_bytes", 0))
    swap_used_str = format_bytes_human(sys_info.get("swap_used_bytes", 0))

    res_table.add_row("Processador (CPU)", render_gauge(sys_info["cpu_percent"]), "Carga global")
    res_table.add_row("Memória RAM", render_gauge(sys_info["memory_percent"]), f"{mem_used_str} / {mem_total_str}")
    res_table.add_row("Memória Swap", render_gauge(sys_info["swap_percent"]), f"{swap_used_str} / {swap_total_str}")

    for disk in sys_info.get("disks", []):
        used_d = format_bytes_human(disk.get("total_bytes", 0) - disk.get("free_bytes", 0))
        tot_d = format_bytes_human(disk.get("total_bytes", 0))
        res_table.add_row(f"Partição ({disk['mountpoint']})", render_gauge(disk["percent"]), f"{used_d} / {tot_d}")

    console.print(
        Panel(
            res_table,
            title=f"[bold {COLOR_PRIMARY_LIGHT}]📊 Monitor de Recursos Físicos[/]",
            border_style=COLOR_BORDER_FOCUS,
            box=CARD_BOX,
        )
    )

    # ─────────────────────────────────────────────────────────────────
    # 4. Principais Processos Consumidores (Vilões)
    # ─────────────────────────────────────────────────────────────────
    top_procs = sys_info.get("top_processes", {})
    cpu_p = top_procs.get("cpu", [])[:3]
    mem_p = top_procs.get("memory", [])[:3]
    swp_p = top_procs.get("swap", [])[:3]

    if cpu_p or mem_p or swp_p:
        proc_table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
        proc_table.add_column("Recurso", width=12, justify="center")
        proc_table.add_column("PID", width=8, justify="right", style=COLOR_TEXT_DIM)
        proc_table.add_column("Processo", ratio=1, style="bold")
        proc_table.add_column("Consumo Registrado", justify="right")

        for p in mem_p:
            rss_str = format_bytes_human(p.get("rss_bytes", 0))
            proc_table.add_row(
                f"[bold white on #7c3aed]  RAM  [/]",
                str(p["pid"]),
                p["name"][:25],
                f"[bold]{p['memory_percent']:.1f}%[/] ({rss_str})",
            )
        for p in swp_p:
            swp_str = format_bytes_human(p.get("swap_bytes", 0))
            proc_table.add_row(
                f"[bold white on #b45309]  SWAP  [/]",
                str(p["pid"]),
                p["name"][:25],
                f"[bold {COLOR_WARNING}]{swp_str}[/]",
            )
        for p in cpu_p:
            if p.get("cpu_percent", 0) > 1.0:
                proc_table.add_row(
                    f"[bold white on #1d4ed8]  CPU  [/]",
                    str(p["pid"]),
                    p["name"][:25],
                    f"[bold]{p['cpu_percent']:.1f}%[/]",
                )

        console.print(
            Panel(
                proc_table,
                title=f"[bold {COLOR_PRIMARY_LIGHT}]🔥 Top Processos Consumidores (Causa Raiz)[/]",
                border_style=COLOR_PRIMARY,
                box=CARD_BOX,
            )
        )

    # ─────────────────────────────────────────────────────────────────
    # 5. Armazenamento: Maiores Diretórios do Sistema (>50 MB)
    # ─────────────────────────────────────────────────────────────────
    disk_hogs = sys_info.get("disk_hogs", [])
    if disk_hogs:
        hog_table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
        hog_table.add_column("Diretório Inspecionado", ratio=2)
        hog_table.add_column("Espaço em Disco", justify="right", style=f"bold {COLOR_WARNING}", ratio=1)

        for hog in disk_hogs[:6]:
            hog_table.add_row(f"📁 {hog['path']}", hog["human_size"])

        console.print(
            Panel(
                hog_table,
                title=f"[bold {COLOR_WARNING}]💾 Pastas com Maior Ocupação de Armazenamento[/]",
                border_style=COLOR_WARNING,
                box=CARD_BOX,
            )
        )

    # ─────────────────────────────────────────────────────────────────
    # 6. Gerenciadores de Pacotes & Repositórios
    # ─────────────────────────────────────────────────────────────────
    pkg_table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
    pkg_table.add_column("Gerenciador", width=24, style="bold")
    pkg_table.add_column("Atualizações Pendentes", justify="center")
    pkg_table.add_column("Segurança", justify="center")

    for mgr_name, mgr_info in packages.get("managers", {}).items():
        tot = mgr_info.get("total", 0)
        sec = mgr_info.get("security", 0)
        tot_badge = f"[bold {COLOR_WARNING}]{tot} pendente(s)[/]" if tot > 0 else "[bold green]✓ Atualizado[/]"
        sec_badge = f"[bold white on #dc2626]  {sec} CRÍTICA(S)  [/]" if sec > 0 else "[dim green]✓ 0 pendentes[/]"
        pkg_table.add_row(f"📦 {mgr_name}", tot_badge, sec_badge)

    console.print(
        Panel(
            pkg_table,
            title=f"[bold {COLOR_PURPLE}]📦 Ecossistema de Pacotes & Atualizações[/]",
            border_style=COLOR_PURPLE,
            box=CARD_BOX,
        )
    )

    # ─────────────────────────────────────────────────────────────────
    # 7. Diagnósticos e Alertas
    # ─────────────────────────────────────────────────────────────────
    if health["items"]:
        diag_table = Table(box=TABLE_BOX, expand=True, padding=(0, 1))
        diag_table.add_column("Severidade", width=14, justify="center")
        diag_table.add_column("Categoria", width=14, style="bold")
        diag_table.add_column("Problema Identificado", ratio=2)
        diag_table.add_column("Ação Recomendada", ratio=3, style=COLOR_TEXT_DIM)

        for item in health["items"]:
            sev_badge = make_badge(item["severity"], level=item["severity"])
            diag_table.add_row(
                sev_badge,
                item["category"],
                f"[bold]{item['title']}[/]\n[dim]{item['message']}[/]",
                item["action"],
            )

        console.print(
            Panel(
                diag_table,
                title="[bold yellow]⚠️ Alertas & Diagnósticos de Sistema[/bold yellow]",
                border_style=COLOR_WARNING,
                box=CARD_BOX,
            )
        )

    # ─────────────────────────────────────────────────────────────────
    # 8. Plano de Ação Recomendado
    # ─────────────────────────────────────────────────────────────────
    act_grid = Table.grid(padding=(0, 1))
    act_grid.add_column(width=4, justify="center")
    act_grid.add_column(style="white")

    for act in health["recommended_actions"]:
        if "[CRÍTICO]" in act:
            act_clean = act.replace("[CRÍTICO]", "").strip()
            act_grid.add_row(f"[{COLOR_DANGER}]▶[/]", f"[bold {COLOR_DANGER}][CRÍTICO][/] {act_clean}")
        elif "[AVISO]" in act:
            act_clean = act.replace("[AVISO]", "").strip()
            act_grid.add_row(f"[{COLOR_WARNING}]▶[/]", f"[bold {COLOR_WARNING}][AVISO][/] {act_clean}")
        else:
            act_grid.add_row(f"[{COLOR_SUCCESS}]✓[/]", f"[green]{act}[/]")

    console.print(
        Panel(
            act_grid,
            title=f"[bold {COLOR_PRIMARY_LIGHT}]📌 Próximos Passos Recomendados[/]",
            border_style=COLOR_PRIMARY,
            box=CARD_BOX,
            padding=(1, 2),
        )
    )
    console.print()


class AlignTextCentral:
    """Classe utilitária para centralização de texto em painéis."""

    def __init__(self, text: str):
        self.text = text

    def __rich__(self):
        return Text.from_markup(self.text, justify="center")
