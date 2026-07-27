"""
Gerenciador de pacotes APK (Alpine Linux).
"""

from typing import Dict, Any, Tuple
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class ApkPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "APK (Alpine Linux)"

    def is_available(self) -> bool:
        return command_exists("apk")

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        run_command(["apk", "update", "-q"], timeout=30)
        code, out, _ = run_command(["apk", "version", "-l", "<"], timeout=30)
        if code == 0 and out:
            lines = [l for l in out.splitlines() if l.strip()]
            result["total"] = len(lines)
            result["details"] = lines[:10]

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "APK não disponível."

        cmds = [
            ["apk", "update"],
            ["apk", "upgrade"],
            ["apk", "cache", "clean"],
        ]

        for cmd in cmds:
            code, out, err = run_command(cmd, dry_run=dry_run, timeout=180)
            if code != 0 and not dry_run:
                return False, f"Erro em {' '.join(cmd)}: {err}"

        return True, "Pacotes APK atualizados com sucesso."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "APK não disponível."
        code, out, _ = run_command(["apk", "cache", "clean"], dry_run=dry_run)
        return code == 0, "Cache do APK limpo."
