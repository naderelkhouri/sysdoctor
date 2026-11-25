"""
Ponto de entrada da interface de linha de comando (CLI) do SysDoctor.
"""

import sys
import os
import argparse
from typing import List, Optional, Tuple
from sysdoctor import __version__
from sysdoctor.utils.logger import setup_logger
from sysdoctor.core.reporter import build_full_report, report_to_json
from sysdoctor.core.cleaner import SystemCleaner
from sysdoctor.package_managers import get_available_package_managers
from sysdoctor.ui.views import display_report, print_banner
from sysdoctor.ui.dashboard import start_live_dashboard
from sysdoctor.ui.selector import (
    arrow_select_menu,
    arrow_checkbox_select,
    wait_for_return,
    MenuItem,
    CheckboxItem,
)
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
    COLOR_TEXT_DIM,
)
from sysdoctor.utils.runner import command_exists, run_command


def check_root_privileges(require_root: bool = False) -> bool:
    """Verifica se o usuário possui privilégios de root (eUID 0)."""
    is_root = os.geteuid() == 0
    if require_root and not is_root:
        console.print(
            f"[bold {COLOR_DANGER}]❌ Esta ação exige privilégios de Administrador (root).[/]"
        )
        console.print(f"[{COLOR_WARNING}]Execute novamente utilizando: sudo sysdoctor ...[/]")
        sys.exit(1)
    return is_root


def send_desktop_notification(report_data: dict):
    """Envia notificação nativa para o desktop via notify-send."""
    if not command_exists("notify-send"):
        return

    score = report_data["health"]["score"]
    status_label = report_data["health"]["status_label"]
    items = report_data["health"]["items"]

    urgency = "critical" if score < 70 or any(i["severity"] == "CRITICAL" for i in items) else "normal"
    icon = "dialog-warning" if score < 70 else "dialog-information"

    title = f"SysDoctor - Saúde: {score}/100 ({status_label})"
    if items:
        body = "\n".join(f"• {i['title']}: {i['message']}" for i in items[:3])
    else:
        body = "Sistema operando perfeitamente."

    sudo_user = os.environ.get("SUDO_USER")
    cmd = ["notify-send", "-u", urgency, "-i", icon, title, body]
    if sudo_user and os.geteuid() == 0:
        uid = os.environ.get("SUDO_UID", "1000")
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS=f"unix:path=/run/user/{uid}/bus")
        run_command(["sudo", "-u", sudo_user] + cmd, env=env, timeout=5)
    else:
        run_command(cmd, timeout=5)


def run_selective_fix(dry_run: bool = False):
    """Permite selecionar com checkboxes e setas quais componentes limpar/corrigir."""
    checkbox_items = [
        CheckboxItem("1", "Gerenciadores de Pacotes (APT / Snap / Flatpak)", "Atualizações e pacotes residuais", True),
        CheckboxItem("2", "Logs do Systemd (Journald)", "Trunca logs com journalctl --vacuum-size=100M", True),
        CheckboxItem("3", "Caches de Desenvolvimento", "Limpa uv, pip, npm, bun e cargo", True),
        CheckboxItem("4", "Cache de Miniaturas", "Limpa miniaturas em ~/.cache/thumbnails", True),
        CheckboxItem("5", "Relatórios de Falhas (/var/crash)", "Remove dumps de travamento do sistema", True),
        CheckboxItem("6", "Docker Prune", "Remove containers e imagens órfãs não utilizadas", False),
        CheckboxItem("7", "Reciclagem de Memória Swap", "Executa swapoff e swapon seguro se houver RAM livre", False),
    ]

    selected_ids = arrow_checkbox_select(
        checkbox_items,
        title="SELEÇÃO GRANULAR DE MANUTENÇÃO",
    )

    if not selected_ids:
        console.print("\n[yellow]Nenhuma opção selecionada ou operação cancelada.[/yellow]")
        return

    cleaner = SystemCleaner(dry_run=dry_run)
    results = []
    console.print(f"\n[bold {COLOR_PRIMARY_LIGHT}]🧹 Executando Tarefas de Manutenção Selecionadas:[/]\n")

    if "1" in selected_ids:
        for mgr in get_available_package_managers():
            with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Atualizando e limpando pacotes ({mgr.name})...[/]", spinner="dots"):
                succ, msg = mgr.auto_fix(dry_run=dry_run)
            status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
            console.print(f" {status} [bold]Pacotes ({mgr.name}):[/] {msg}")
            results.append((f"Pacotes ({mgr.name})", succ, msg))

    if "2" in selected_ids:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Truncando logs do Systemd Journal (limite 100M)...[/]", spinner="dots"):
            succ, msg = cleaner.vacuum_journal_logs()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Systemd Journal:[/] {msg}")
        results.append(("Systemd Journal", succ, msg))

    if "3" in selected_ids:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Limpando caches de desenvolvimento (uv, pip, npm, bun, cargo)...[/]", spinner="dots"):
            succ, msg = cleaner.clean_dev_caches()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Caches Dev:[/] {msg}")
        results.append(("Caches Dev", succ, msg))

    if "4" in selected_ids:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Limpando miniaturas e caches de usuário...[/]", spinner="dots"):
            succ, msg = cleaner.clean_user_caches()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Miniaturas:[/] {msg}")
        results.append(("Miniaturas", succ, msg))

    if "5" in selected_ids:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Removendo relatórios de falha em /var/crash...[/]", spinner="dots"):
            succ, msg = cleaner.clean_crash_reports()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Crash Reports:[/] {msg}")
        results.append(("Crash Reports", succ, msg))

    if "6" in selected_ids:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Executando Docker Prune (containers e imagens órfãs)...[/]", spinner="dots"):
            succ, msg = cleaner.clean_docker_containers()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Docker Prune:[/] {msg}")
        results.append(("Docker Prune", succ, msg))

    if "7" in selected_ids:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Reciclando memória Swap com segurança (swapoff/swapon)...[/]", spinner="dots"):
            succ, msg = cleaner.recycle_swap()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Reciclar Swap:[/] {msg}")
        results.append(("Reciclar Swap", succ, msg))

    console.print(f"\n[bold green]✔ Tarefas de manutenção concluídas![/bold green]")


def run_automated_maintenance(dry_run: bool = False) -> List[Tuple[str, bool, str]]:
    """Executa a auto-correção completa com animações e feedback instantâneo de cada etapa."""
    cleaner = SystemCleaner(dry_run=dry_run)
    results = []

    # 1. Gerenciadores de Pacotes
    for mgr in get_available_package_managers():
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Atualizando pacotes e dependências ({mgr.name})...[/]", spinner="dots"):
            succ, msg = mgr.auto_fix(dry_run=dry_run)
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Pacotes ({mgr.name}):[/] {msg}")
        results.append((f"Pacotes ({mgr.name})", succ, msg))

    # 2. Journald
    with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Truncando logs do Systemd Journal (limite 100M)...[/]", spinner="dots"):
        succ, msg = cleaner.vacuum_journal_logs()
    status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
    console.print(f" {status} [bold]Systemd Journal:[/] {msg}")
    results.append(("Systemd Journal", succ, msg))

    # 3. User Caches
    with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Limpando caches de miniaturas do usuário...[/]", spinner="dots"):
        succ, msg = cleaner.clean_user_caches()
    status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
    console.print(f" {status} [bold]Miniaturas:[/] {msg}")
    results.append(("Miniaturas", succ, msg))

    # 4. Dev Caches
    with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Limpando caches de desenvolvimento (uv, pip, npm, bun, cargo)...[/]", spinner="dots"):
        succ, msg = cleaner.clean_dev_caches()
    status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
    console.print(f" {status} [bold]Caches Dev:[/] {msg}")
    results.append(("Caches Dev", succ, msg))

    # 5. Crash Reports
    with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Removendo relatórios de falhas (/var/crash)...[/]", spinner="dots"):
        succ, msg = cleaner.clean_crash_reports()
    status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
    console.print(f" {status} [bold]Crash Reports:[/] {msg}")
    results.append(("Crash Reports", succ, msg))

    # 6. Docker
    if command_exists("docker"):
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Executando Docker System Prune...[/]", spinner="dots"):
            succ, msg = cleaner.clean_docker_containers()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f" {status} [bold]Containers Docker:[/] {msg}")
        results.append(("Containers Docker", succ, msg))

    # 8. Swap
    if os.geteuid() == 0:
        try:
            import psutil
            if psutil.swap_memory().percent > 70:
                with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Reciclando memória Swap com segurança...[/]", spinner="dots"):
                    succ, msg = cleaner.recycle_swap()
                status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
                console.print(f" {status} [bold]Reciclagem Swap:[/] {msg}")
                results.append(("Reciclagem Swap", succ, msg))
        except Exception:
            pass

    console.print(f"\n[bold green]✔ Manutenção finalizada com sucesso![/bold green]")
    return results


def show_interactive_menu():
    """Menu interativo navegável por setas direcionais ou atalhos numéricos."""
    menu_items = [
        MenuItem("1", "🩺 Relatório de Saúde", "Inspeção profunda, Top vilões e cálculo do Health Score", "Normal"),
        MenuItem("2", "🔧 Auto-Correção Completa", "Atualização geral, expurgo de caches e limpeza automatizada", "Sudo"),
        MenuItem("3", "🎯 Limpeza Seletiva", "Seleção interativa com checkboxes (espaço/setas)", "Sudo"),
        MenuItem("4", "🔄 Reciclar Memória Swap", "Esvaziamento seguro e restauração do swap em disco", "Sudo"),
        MenuItem("5", "📊 Monitor ao Vivo (TUI)", "Painel em tempo real estilo htop/btop com consumo de processos", "Normal"),
        MenuItem("6", "📄 Exportar em JSON", "Gera a estrutura completa de métricas para logging e scripting", "Normal"),
        MenuItem("0", "🚪 Encerrar", "Sair do SysDoctor", "—"),
    ]

    while True:
        choice = arrow_select_menu(
            menu_items,
            title="CENTRAL DE OPERAÇÕES DO SISTEMA",
            subtitle="Navegue com [↑/↓] e confirme com [Enter]",
        )

        try:
            if choice == "1":
                with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Gerando diagnóstico completo do sistema...[/]", spinner="dots"):
                    report = build_full_report()
                console.clear()
                display_report(report)
                wait_for_return()
            elif choice == "2":
                check_root_privileges(require_root=True)
                console.clear()
                console.print(f"[bold {COLOR_PRIMARY_LIGHT}]🧹 Iniciando Auto-Correção Completa...[/]\n")
                run_automated_maintenance(dry_run=False)
                wait_for_return()
            elif choice == "3":
                check_root_privileges(require_root=True)
                console.clear()
                run_selective_fix(dry_run=False)
                wait_for_return()
            elif choice == "4":
                check_root_privileges(require_root=True)
                console.clear()
                console.print(f"[bold {COLOR_PRIMARY_LIGHT}]🔄 Tentando reciclar a memória Swap com segurança...[/]\n")
                with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Executando swapoff e swapon seguro...[/]", spinner="dots"):
                    cleaner = SystemCleaner(dry_run=False)
                    succ, msg = cleaner.recycle_swap()
                status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
                console.print(f" {status} {msg}")
                wait_for_return()
            elif choice == "5":
                start_live_dashboard()
            elif choice == "6":
                with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Compilando dados para JSON...[/]", spinner="dots"):
                    report = build_full_report()
                console.clear()
                console.print(report_to_json(report))
                wait_for_return()
            elif choice in ("0", "exit", "q", "sair"):
                console.print(f"[{COLOR_PRIMARY_LIGHT}]Até logo![/]")
                break
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Operação cancelada.[/yellow]")
            break


def main(args_list: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        prog="sysdoctor",
        description="SysDoctor - Diagnóstico, Monitoramento e Manutenção Automatizada para Linux.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"sysdoctor {__version__}"
    )
    parser.add_argument(
        "-r", "--report", action="store_true", help="Gera e exibe o relatório de saúde completo."
    )
    parser.add_argument(
        "-f", "--fix", "--auto-fix", action="store_true", dest="fix", help="Executa auto-correção e limpeza automatizada do sistema."
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Executa a limpeza em modo de seleção interativa."
    )
    parser.add_argument(
        "--recycle-swap", action="store_true", help="Recicla e esvazia a memória Swap com segurança."
    )
    parser.add_argument(
        "--notify", action="store_true", help="Envia notificação nativa para a área de trabalho."
    )
    parser.add_argument(
        "-m", "--monitor", action="store_true", help="Inicia o monitor interativo em tempo real (TUI)."
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="Exibe o relatório em formato JSON estruturado."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simula operações sem aplicar alterações reais no sistema."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Ativa logs detalhados de depuração."
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Responde sim para todas as confirmações não interativas."
    )

    parsed = parser.parse_args(args_list)
    setup_logger(parsed.verbose)

    # Notificação Desktop
    if parsed.notify:
        report = build_full_report()
        send_desktop_notification(report)
        return

    # Execução baseada em flags
    if parsed.json:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Coletando dados do sistema...[/]", spinner="dots"):
            report = build_full_report()
        print(report_to_json(report))
        return

    if parsed.report:
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Gerando diagnóstico de saúde do sistema...[/]", spinner="dots"):
            report = build_full_report()
        display_report(report)
        return

    if parsed.monitor:
        start_live_dashboard()
        return

    if parsed.recycle_swap:
        if not parsed.dry_run:
            check_root_privileges(require_root=True)
        with console.status(f"[bold {COLOR_PRIMARY_LIGHT}]Reciclando memória Swap com segurança (swapoff/swapon)...[/]", spinner="dots"):
            cleaner = SystemCleaner(dry_run=parsed.dry_run)
            succ, msg = cleaner.recycle_swap()
        status = "[bold green]✓[/bold green]" if succ else f"[bold {COLOR_DANGER}]✗[/bold {COLOR_DANGER}]"
        console.print(f"{status} {msg}")
        return

    if parsed.interactive:
        if not parsed.dry_run:
            check_root_privileges(require_root=True)
        run_selective_fix(dry_run=parsed.dry_run)
        return

    if parsed.fix:
        if not parsed.dry_run:
            check_root_privileges(require_root=True)
        console.print(f"[bold {COLOR_PRIMARY_LIGHT}]🧹 Iniciando Auto-Correção Completa do Sistema...[/]\n")
        run_automated_maintenance(dry_run=parsed.dry_run)
        return

    # Se nenhuma flag for informada, abre o menu interativo
    show_interactive_menu()


if __name__ == "__main__":
    main()
