"""
Gerenciador de pacotes APT (Debian, Ubuntu, Mint, Pop!_OS, etc.).
"""

import os
from typing import Dict, Any, Tuple, List
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.utils.runner import command_exists, run_command


class AptPackageManager(BasePackageManager):
    PROTECTED_RESIDUAL_KEYWORDS = (
        "grub",
        "shim",
        "efibootmgr",
        "systemd",
        "udev",
        "linux-image",
        "linux-modules",
        "plymouth",
    )

    @property
    def name(self) -> str:
        return "APT (Debian/Ubuntu)"

    def is_available(self) -> bool:
        return command_exists("apt-get")

    def get_residual_packages(self) -> List[str]:
        """Retorna a lista de pacotes com status 'rc' (removidos mas com configs residuais)."""
        if not command_exists("dpkg"):
            return []
        code, out, _ = run_command(["dpkg", "-l"], timeout=30)
        if code != 0 or not out:
            return []

        packages = []
        for line in out.splitlines():
            if line.startswith("rc"):
                parts = line.split()
                if len(parts) >= 2:
                    packages.append(parts[1])
        return packages

    def clean_residual_packages(self, dry_run: bool = False) -> Tuple[bool, str]:
        """
        Remove com segurança pacotes em estado 'rc' (configurações residuais),
        filtrando estritamente pacotes críticos de bootloader e kernel
        para evitar perda de arquivos essenciais de inicialização (como /boot/grub).
        """
        if not command_exists("dpkg"):
            return False, "dpkg não está disponível."

        residuals = self.get_residual_packages()
        if not residuals:
            return True, "Nenhum pacote residual (rc) encontrado."

        safe_to_purge = [
            pkg for pkg in residuals
            if not any(crit in pkg.lower() for crit in self.PROTECTED_RESIDUAL_KEYWORDS)
        ]

        ignored_count = len(residuals) - len(safe_to_purge)
        if not safe_to_purge:
            return True, f"Nenhum pacote residual seguro para expurgar ({ignored_count} pacotes críticos de boot/kernel preservados)."

        env = dict(os.environ, DEBIAN_FRONTEND="noninteractive")
        cmd = ["dpkg", "--purge"] + safe_to_purge
        code, out, err = run_command(cmd, env=env, dry_run=dry_run, timeout=120)
        if code == 0:
            msg = f"{len(safe_to_purge)} pacotes residuais limpos com segurança."
            if ignored_count > 0:
                msg += f" ({ignored_count} pacotes críticos de boot/kernel protegidos)."
            return True, msg
        return False, f"Falha ao expurgar pacotes residuais: {err}"

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

        # Limpeza segura de configurações residuais (rc)
        succ_rc, msg_rc = self.clean_residual_packages(dry_run=dry_run)
        if succ_rc:
            logs.append(f"✓ {msg_rc}")
        else:
            logs.append(f"⚠ {msg_rc}")

        return True, "Pacotes APT atualizados e limpos com sucesso."

    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "APT não disponível."
        code, out, err = run_command(["apt-get", "clean"], dry_run=dry_run)
        return code == 0, out or "Cache do APT limpo."
