import os
import pwd
import shutil
from pathlib import Path
from typing import List, Tuple
from sysdoctor.package_managers import get_available_package_managers
from sysdoctor.utils.runner import command_exists, run_command


def get_target_user_home() -> Path:
    """Retorna o diretório home do usuário real (mesmo se executado com sudo)."""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except Exception:
            pass
    return Path.home()


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
        """Limpa miniaturas e caches temporários no ambiente do usuário."""
        home = get_target_user_home()
        thumbnails_dir = home / ".cache" / "thumbnails"

        if not thumbnails_dir.exists():
            return True, "Nenhum cache de miniaturas encontrado."

        if self.dry_run:
            return True, f"[DRY-RUN] Miniaturas em {thumbnails_dir} seriam limpas."

        try:
            cleaned = 0
            for item in thumbnails_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    cleaned += 1
                elif item.is_file():
                    item.unlink(missing_ok=True)
                    cleaned += 1
            return True, f"Cache de miniaturas limpo ({cleaned} itens removidos)."
        except Exception as e:
            return False, f"Falha ao limpar miniaturas: {e}"

    def clean_dev_caches(self) -> Tuple[bool, str]:
        """
        Limpa caches de ferramentas de desenvolvimento comuns (uv, pip, npm),
        que costumam ser grandes responsáveis pelo esgotamento de disco.
        """
        cleaned_tools = []
        sudo_user = os.environ.get("SUDO_USER")

        def run_tool(cmd_list: List[str]) -> Tuple[int, str, str]:
            if sudo_user and os.geteuid() == 0 and command_exists("sudo"):
                cmd_to_run = ["sudo", "-u", sudo_user] + cmd_list
            else:
                cmd_to_run = cmd_list
            return run_command(cmd_to_run, dry_run=self.dry_run, timeout=60)

        # 1. uv cache clean
        if command_exists("uv"):
            code, _, _ = run_tool(["uv", "cache", "clean"])
            if code == 0:
                cleaned_tools.append("uv")

        # 2. pip / pip3 cache purge
        pip_cmd = "pip" if command_exists("pip") else ("pip3" if command_exists("pip3") else None)
        if pip_cmd:
            code, _, _ = run_tool([pip_cmd, "cache", "purge"])
            if code == 0:
                cleaned_tools.append(pip_cmd)

        # 3. npm cache clean --force
        if command_exists("npm"):
            code, _, _ = run_tool(["npm", "cache", "clean", "--force"])
            if code == 0:
                cleaned_tools.append("npm")

        if cleaned_tools:
            return True, f"Caches de desenvolvimento limpos com sucesso ({', '.join(cleaned_tools)})."
        return True, "Nenhuma ferramenta de desenvolvimento ativa com cache para limpar."

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

        # 4. Dev Caches (uv, pip, npm)
        succ_d, msg_d = self.clean_dev_caches()
        results.append(("Caches de Desenvolvimento", succ_d, msg_d))

        return results
