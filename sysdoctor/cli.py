"""
Ponto de entrada da interface de linha de comando (CLI) do SysDoctor.
"""

import sys
import os
import argparse
from typing import List, Optional
from sysdoctor import __version__
from sysdoctor.utils.logger import setup_logger
from sysdoctor.core.reporter import build_full_report, report_to_json
from sysdoctor.core.cleaner import SystemCleaner
from sysdoctor.ui.views import display_report, print_banner
from sysdoctor.ui.dashboard import start_live_dashboard
from sysdoctor.ui.theme import console


def check_root_privileges(require_root: bool = False) -> bool:
    """Verifica se o usuário possui privilégios de root (eUID 0)."""
    is_root = os.geteuid() == 0
    if require_root and not is_root:
        console.print(
            "[bold red]❌ Esta ação exige privilégios de Administrador (root).[/bold red]"
        )
        console.print("[yellow]Execute novamente utilizando: sudo sysdoctor ...[/yellow]")
        sys.exit(1)
    return is_root


def show_interactive_menu():
    """Menu interativo quando o programa é executado sem argumentos."""
    while True:
        console.clear()
        print_banner()
        console.print(
            """[bold cyan]
╔══════════════════════════════════════════╗
║ 1 🩺 Relatório Completo de Saúde         ║
║ 2 🔧 Auto-Correção e Limpeza do Sistema  ║
║ 3 📊 Monitor em Tempo Real (Live TUI)    ║
║ 4 📄 Exportar Relatório em JSON          ║
║ 0 🚪 Sair                                ║
╚══════════════════════════════════════════╝
[/bold cyan]"""
        )
        try:
            choice = input("sysdoctor > ").strip()
            if choice == "1":
                report = build_full_report()
                console.clear()
                display_report(report)
                input("\nPressione Enter para retornar ao menu...")
            elif choice == "2":
                check_root_privileges(require_root=True)
                console.clear()
                console.print("[bold cyan]🧹 Iniciando Auto-Correção e Limpeza...[/bold cyan]\n")
                cleaner = SystemCleaner(dry_run=False)
                results = cleaner.run_full_autofix()
                for name, succ, msg in results:
                    status = "[bold green]✓[/bold green]" if succ else "[bold red]✗[/bold red]"
                    console.print(f"{status} {name}: {msg}")
                console.print("\n[bold green]✔ Manutenção concluída![/bold green]")
                input("\nPressione Enter para retornar ao menu...")
            elif choice == "3":
                start_live_dashboard()
            elif choice == "4":
                report = build_full_report()
                console.clear()
                console.print(report_to_json(report))
                input("\nPressione Enter para retornar ao menu...")
            elif choice in ("0", "exit", "q", "sair"):
                console.print("[cyan]Até logo![/cyan]")
                break
        except (KeyboardInterrupt, EOFError):
            console.print("\n[cyan]Operação cancelada.[/cyan]")
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

    # Execução baseada em flags
    if parsed.json:
        report = build_full_report()
        print(report_to_json(report))
        return

    if parsed.report:
        report = build_full_report()
        display_report(report)
        return

    if parsed.monitor:
        start_live_dashboard()
        return

    if parsed.fix:
        if not parsed.dry_run:
            check_root_privileges(require_root=True)
        console.print("[bold cyan]🧹 Executando Auto-Correção do Sistema...[/bold cyan]\n")
        cleaner = SystemCleaner(dry_run=parsed.dry_run)
        results = cleaner.run_full_autofix()
        for name, succ, msg in results:
            status = "[bold green]✓[/bold green]" if succ else "[bold red]✗[/bold red]"
            console.print(f"{status} {name}: {msg}")
        console.print("\n[bold green]✔ Manutenção finalizada com sucesso![/bold green]")
        return

    # Se nenhuma flag for informada, abre o menu interativo
    show_interactive_menu()


if __name__ == "__main__":
    main()
