"""
Gerenciador de pacotes Pacman (Arch Linux, Manjaro, EndeavourOS, etc.).
"""

from typing import Dict, Any, Tuple
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class PacmanPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "Pacman (Arch Linux)"

    def is_available(self) -> bool:
        return command_exists("pacman")

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        # Verifica pacotes pendentes utilizando checkupdates (se instalado) ou pacman -Qu
        if command_exists("checkupdates"):
            code, out, _ = run_command(["checkupdates"], timeout=60)
        else:
            code, out, _ = run_command(["pacman", "-Qu"], timeout=30)

        if code == 0 and out:
            lines = [l for l in out.splitlines() if l.strip()]
            result["total"] = len(lines)
            result["details"] = lines[:10]

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Pacman não está disponível."

        cmds = [
            ["pacman", "-Syu", "--noconfirm"],
        ]

        # Remoção de órfãos se existirem
        code_orph, out_orph, _ = run_command(["pacman", "-Qtdq"], timeout=15)
        if code_orph == 0 and out_orph:
            orphans = out_orph.splitlines()
            if orphans:
                cmds.append(["pacman", "-Rns", "--noconfirm"] + orphans)

        for cmd in cmds:
            code, out, err = run_command(cmd, dry_run=dry_run, timeout=300)
            if code != 0 and not dry_run:
                return False, f"Erro em {' '.join(cmd)}: {err}"

        return True, "Pacotes Pacman atualizados com sucesso."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Pacman não disponível."
        code, out, _ = run_command(["pacman", "-Sc", "--noconfirm"], dry_run=dry_run)
        return code == 0, "Cache do Pacman limpo."
