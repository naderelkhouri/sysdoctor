"""
Gerenciador de pacotes APT (Debian, Ubuntu, Mint, Pop!_OS, etc.).
"""

import os
from typing import Dict, Any, Tuple
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class AptPackageManager(BasePackageManager):
    @property
    def name(self) -> str:
        return "APT (Debian/Ubuntu)"

    def is_available(self) -> bool:
        return command_exists("apt-get")

    def check_updates(self) -> Dict[str, Any]:
        result = {"total": 0, "security": 0, "phased": False, "details": []}
        if not self.is_available():
            return result

        # Atualiza o índice silenciosamente se possível
        run_command(["apt-get", "update", "-qq"], timeout=60)

        # Pacientes atualizáveis
        code, out, _ = run_command(["apt", "list", "--upgradable"], timeout=30)
        if code == 0 and out:
            lines = [l for l in out.splitlines() if "/" in l and not l.startswith("Listing...")]
            result["total"] = len(lines)
            result["details"] = lines[:10]  # Limita as primeiras 10 para o relatório

        # Verificação de segurança simulada
        code_sec, out_sec, _ = run_command(["apt-get", "-s", "upgrade"], timeout=30)
        if code_sec == 0 and out_sec:
            sec_lines = [l for l in out_sec.splitlines() if "security" in l.lower() or "sec" in l.lower()]
            result["security"] = len(sec_lines)

        # Verificação de atualizações faseadas
        code_full, out_full, _ = run_command(["apt-get", "-s", "full-upgrade"], timeout=30)
        if code_full == 0 and out_full:
            result["phased"] = "faseamento" in out_full.lower() or "phased" in out_full.lower()

        return result

    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "APT não está disponível."

        env = dict(os.environ, DEBIAN_FRONTEND="noninteractive")
        cmds = [
            ["apt-get", "update"],
            ["apt-get", "full-upgrade", "-y", "-o", "Dpkg::Options::=--force-confdef", "-o", "Dpkg::Options::=--force-confold"],
            ["apt-get", "autoremove", "-y"],
            ["apt-get", "autoclean", "-y"],
            ["apt-get", "clean"],
        ]

        logs = []
        for cmd in cmds:
            code, out, err = run_command(cmd, env=env, dry_run=dry_run, timeout=300)
            if code != 0 and not dry_run:
                logs.append(f"Erro em {' '.join(cmd)}: {err}")
                return False, "\n".join(logs)
            logs.append(f"✓ Sucesso: {' '.join(cmd)}")

        return True, "Pacotes APT atualizados e limpos com sucesso."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "APT não disponível."
        code, out, err = run_command(["apt-get", "clean"], dry_run=dry_run)
        return code == 0, out or "Cache do APT limpo."
