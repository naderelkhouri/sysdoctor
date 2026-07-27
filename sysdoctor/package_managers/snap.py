"""
Gerenciador de pacotes Snap.
"""

from typing import Dict, Any, Tuple, List
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class SnapPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "Snap"

    def is_available(self) -> bool:
        return command_exists("snap")

    def get_disabled_revisions(self) -> List[Tuple[str, str]]:
        """Retorna uma lista de tuplas (nome, revisão) de snaps desativados."""
        if not self.is_available():
            return []
        code, out, _ = run_command(["snap", "list", "--all"], timeout=30)
        if code != 0 or not out:
            return []

        disabled = []
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 6 and parts[-1] == "disabled":
                disabled.append((parts[0], parts[2]))
        return disabled

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        disabled = self.get_disabled_revisions()
        result["total"] = len(disabled)
        if disabled:
            result["details"] = [f"{name} (rev {rev} desativado)" for name, rev in disabled[:10]]

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Snap não está disponível."

        run_command(["snap", "refresh"], dry_run=dry_run, timeout=300)

        disabled = self.get_disabled_revisions()
        cleaned_count = 0
        for name, rev in disabled:
            code, _, _ = run_command(["snap", "remove", name, "--revision", rev], dry_run=dry_run)
            if code == 0:
                cleaned_count += 1

        return True, f"Snap atualizado. {cleaned_count} revisões antigas removidas."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        return self.auto_fix(dry_run=dry_run)
