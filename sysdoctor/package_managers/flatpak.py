"""
Gerenciador de pacotes Flatpak.
"""

from typing import Dict, Any, Tuple
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class FlatpakPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "Flatpak"

    def is_available(self) -> bool:
        return command_exists("flatpak")

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        code, out, _ = run_command(["flatpak", "remote-ls", "--updates"], timeout=60)
        if code == 0 and out:
            lines = [l for l in out.splitlines() if l.strip()]
            result["total"] = len(lines)
            result["details"] = lines[:10]

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Flatpak não está disponível."

        run_command(["flatpak", "update", "-y"], dry_run=dry_run, timeout=300)
        run_command(["flatpak", "uninstall", "--unused", "-y"], dry_run=dry_run, timeout=120)

        return True, "Flatpaks atualizados e runtimes não utilizados removidos."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Flatpak não disponível."
        code, out, _ = run_command(["flatpak", "uninstall", "--unused", "-y"], dry_run=dry_run)
        return code == 0, "Runtimes não utilizadas do Flatpak removidas."
