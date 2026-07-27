"""
Gerenciador de pacotes Zypper (openSUSE).
"""

from typing import Dict, Any, Tuple
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class ZypperPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "Zypper (openSUSE)"

    def is_available(self) -> bool:
        return command_exists("zypper")

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        code, out, _ = run_command(["zypper", "--non-interactive", "list-updates"], timeout=60)
        if code == 0 and out:
            lines = [l for l in out.splitlines() if "|" in l and "v |" in l]
            result["total"] = len(lines)
            result["details"] = lines[:10]

        code_sec, out_sec, _ = run_command(["zypper", "--non-interactive", "patch-check"], timeout=60)
        if code_sec == 0 and out_sec and "security" in out_sec.lower():
            result["security"] = 1

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Zypper não disponível."

        cmds = [
            ["zypper", "--non-interactive", "refresh"],
            ["zypper", "--non-interactive", "update", "-y"],
            ["zypper", "--non-interactive", "clean"],
        ]

        for cmd in cmds:
            code, out, err = run_command(cmd, dry_run=dry_run, timeout=300)
            if code != 0 and not dry_run:
                return False, f"Erro em {' '.join(cmd)}: {err}"

        return True, "Pacotes Zypper atualizados com sucesso."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Zypper não disponível."
        code, out, _ = run_command(["zypper", "--non-interactive", "clean"], dry_run=dry_run)
        return code == 0, "Cache do Zypper limpo."
