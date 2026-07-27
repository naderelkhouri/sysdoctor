"""
Módulo de limpeza profunda e auto-correção do sistema.
"""

from typing import List, Tuple
from sysdoctor.package_managers import get_available_package_managers
from sysdoctor.utils.runner import command_exists, run_command


class SystemCleaner:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def vacuum_journal_logs(self, max_size: str = "100M") -> Tuple[bool, str]:
        """Reduz o tamanho dos logs do systemd journald."""
        if not command_exists("journalctl"):
            return False, "journalctl não disponível."

        code, out, err = run_command(
            ["journalctl", f"--vacuum-size={max_size}"], dry_run=self.dry_run, timeout=60
        )
        if code == 0:
            return True, f"Logs do journald truncados para no máximo {max_size}."
        return False, f"Falha ao truncar logs: {err}"

    def clean_user_caches(self) -> Tuple[bool, str]:
        """Limpa miniaturas e caches temporários no ambiente do usuário (se aplicável)."""
        # Limpeza simples de cache de miniaturas (thumbnails)
        code, out, _ = run_command(
            ["rm", "-rf", "~/.cache/thumbnails/*"], dry_run=self.dry_run, timeout=30
        )
        return True, "Caches de miniaturas limpos."

    def run_full_autofix(self) -> List[Tuple[str, bool, str]]:
        """
        Executa auto-correção em todos os gerenciadores de pacotes e no sistema.
        Retorna lista de resultados: [(nome_componente, sucesso, mensagem)]
        """
        results = []

        # 1. Gerenciadores de Pacotes
        managers = get_available_package_managers()
        for mgr in managers:
            success, msg = mgr.auto_fix(dry_run=self.dry_run)
            results.append((f"Gerenciador {mgr.name}", success, msg))

        # 2. Vacuum Journald Logs
        succ_j, msg_j = self.vacuum_journal_logs()
        results.append(("Systemd Journal Logs", succ_j, msg_j))

        # 3. User Cache
        succ_c, msg_c = self.clean_user_caches()
        results.append(("Cache de Miniaturas", succ_c, msg_c))

        return results
