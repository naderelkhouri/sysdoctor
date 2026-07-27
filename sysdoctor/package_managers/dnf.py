"""
Gerenciador de pacotes DNF/YUM (Fedora, RHEL, CentOS, Rocky Linux, etc.).
"""

from typing import Dict, Any, Tuple
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class DnfPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "DNF (Fedora/RHEL)"

    def is_available(self) -> bool:
        return command_exists("dnf") or command_exists("yum")

    def _get_bin(self) -> str:
        return "dnf" if command_exists("dnf") else "yum"

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        bin_cmd = self._get_bin()
        code, out, _ = run_command([bin_cmd, "check-update", "-q"], timeout=60)
        # dnf check-update retorna 100 se houver atualizações
        if code in (0, 100) and out:
            lines = [l for l in out.splitlines() if l and not l.startswith(" ")]
            result["total"] = len(lines)
            result["details"] = lines[:10]

        code_sec, out_sec, _ = run_command([bin_cmd, "check-update", "--security", "-q"], timeout=60)
        if code_sec in (0, 100) and out_sec:
            sec_lines = [l for l in out_sec.splitlines() if l and not l.startswith(" ")]
            result["security"] = len(sec_lines)

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "DNF/YUM não está disponível."

        bin_cmd = self._get_bin()
        cmds = [
            [bin_cmd, "upgrade", "-y"],
            [bin_cmd, "autoremove", "-y"],
            [bin_cmd, "clean", "all"],
        ]

        for cmd in cmds:
            code, out, err = run_command(cmd, dry_run=dry_run, timeout=300)
            if code != 0 and not dry_run:
                return False, f"Erro em {' '.join(cmd)}: {err}"

        return True, "Pacotes DNF/YUM atualizados com sucesso."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "DNF/YUM não disponível."
        bin_cmd = self._get_bin()
        code, out, _ = run_command([bin_cmd, "clean", "all"], dry_run=dry_run)
        return code == 0, "Cache do DNF limpo."
