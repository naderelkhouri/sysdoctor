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

        # 4. bun cache
        home = get_target_user_home()
        bun_cache_dir = home / ".bun" / "install" / "cache"
        if command_exists("bun") or bun_cache_dir.exists():
            if self.dry_run:
                cleaned_tools.append("bun")
            else:
                if bun_cache_dir.exists():
                    try:
                        shutil.rmtree(bun_cache_dir, ignore_errors=True)
                        bun_cache_dir.mkdir(parents=True, exist_ok=True)
                        cleaned_tools.append("bun")
                    except Exception:
                        pass
                elif command_exists("bun"):
                    code, _, _ = run_tool(["bun", "pm", "cache", "rm"])
                    if code == 0:
                        cleaned_tools.append("bun")

        # 5. cargo (Rust) registry cache
        cargo_cache_dir = home / ".cargo" / "registry" / "cache"
        if cargo_cache_dir.exists():
            if self.dry_run:
                cleaned_tools.append("cargo")
            else:
                try:
                    shutil.rmtree(cargo_cache_dir, ignore_errors=True)
                    cargo_cache_dir.mkdir(parents=True, exist_ok=True)
                    cleaned_tools.append("cargo")
                except Exception:
                    pass

        if cleaned_tools:
            return True, f"Caches de desenvolvimento limpos com sucesso ({', '.join(cleaned_tools)})."
        return True, "Nenhuma ferramenta de desenvolvimento ativa com cache para limpar."

    def clean_crash_reports(self) -> Tuple[bool, str]:
        """Remove relatórios de falhas do sistema em /var/crash/."""
        crash_dir = Path("/var/crash")
        if not crash_dir.exists():
            return True, "Nenhum diretório /var/crash encontrado."

        try:
            files = list(crash_dir.iterdir())
            if not files:
                return True, "Nenhum relatório de falha em /var/crash."

            if self.dry_run:
                return True, f"[DRY-RUN] {len(files)} relatórios de falha seriam removidos de /var/crash."

            removed = 0
            for f in files:
                try:
                    if f.is_file() or f.is_symlink():
                        f.unlink(missing_ok=True)
                        removed += 1
                    elif f.is_dir():
                        shutil.rmtree(f, ignore_errors=True)
                        removed += 1
                except Exception:
                    pass
            return True, f"{removed} relatório(s) de falha removido(s) de /var/crash."
        except Exception as e:
            return False, f"Falha ao limpar /var/crash: {e}"

    def clean_flatpak_unused(self) -> Tuple[bool, str]:
        """Remove runtimes órfãos do Flatpak."""
        if not command_exists("flatpak"):
            return True, "Flatpak não instalado."

        if self.dry_run:
            return True, "[DRY-RUN] Runtimes não utilizados do Flatpak seriam removidos."

        code, out, err = run_command(["flatpak", "uninstall", "--unused", "-y"], timeout=180)
        if code == 0:
            return True, "Runtimes órfãos do Flatpak removidos com sucesso."
        return False, f"Falha ao remover runtimes do Flatpak: {err}"

    def recycle_swap(self) -> Tuple[bool, str]:
        """
        Recicla a memória swap executando swapoff e swapon,
        desde que haja memória RAM disponível suficiente para acomodar os dados.
        """
        if not command_exists("swapoff") or not command_exists("swapon"):
            return False, "Comandos swapoff/swapon não disponíveis."

        if os.geteuid() != 0:
            return False, "Reciclagem de swap exige privilégios de root (sudo)."

        try:
            import psutil
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            if swap.used == 0:
                return True, "Memória swap já está desocupada (0 bytes em uso)."

            # Margem de segurança: memória disponível deve ser superior ao swap usado + 512MB
            safety_margin = 512 * 1024 * 1024
            if mem.available < (swap.used + safety_margin):
                return (
                    False,
                    f"RAM livre insuficiente ({mem.available / (1024**3):.1f} GB) "
                    f"para absorver {swap.used / (1024**3):.1f} GB de Swap com segurança.",
                )

            if self.dry_run:
                return True, f"[DRY-RUN] Swapoff e Swapon seriam executados para liberar {swap.used / (1024**3):.1f} GB."

            code_off, _, err_off = run_command(["swapoff", "-a"], timeout=180)
            if code_off != 0:
                # Tenta religar imediatamente em caso de falha
                run_command(["swapon", "-a"], timeout=60)
                return False, f"Falha ao desativar swap: {err_off}"

            code_on, _, err_on = run_command(["swapon", "-a"], timeout=60)
            if code_on != 0:
                return False, f"Falha ao reativar swap: {err_on}"

            return True, "Memória Swap reciclada com sucesso (swapoff/swapon)."
        except Exception as e:
            return False, f"Erro ao reciclar swap: {e}"

    def clean_docker_containers(self) -> Tuple[bool, str]:
        """Remove containers parados, volumes e redes não utilizados do Docker."""
        if not command_exists("docker"):
            return True, "Docker não instalado."

        # Checa se daemon está ativo
        code_info, _, _ = run_command(["docker", "info"], timeout=10)
        if code_info != 0:
            return True, "Docker daemon inativo."

        if self.dry_run:
            return True, "[DRY-RUN] Recursos não utilizados do Docker seriam limpos."

        code, out, err = run_command(["docker", "system", "prune", "-f"], timeout=120)
        if code == 0:
            return True, "Containers e imagens órfãs do Docker limpos com sucesso."
        return False, f"Falha na limpeza do Docker: {err}"

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

        # 4. Dev Caches (uv, pip, npm, bun, cargo)
        succ_d, msg_d = self.clean_dev_caches()
        results.append(("Caches de Desenvolvimento", succ_d, msg_d))

        # 5. Relatórios de Falhas (/var/crash)
        succ_cr, msg_cr = self.clean_crash_reports()
        results.append(("Relatórios de Falhas", succ_cr, msg_cr))

        # 6. Docker Containers (se ativo)
        if command_exists("docker"):
            succ_dk, msg_dk = self.clean_docker_containers()
            results.append(("Containers Docker", succ_dk, msg_dk))

        # 8. Reciclagem Oportunística de Swap (se swap > 70%)
        if os.geteuid() == 0:
            try:
                import psutil
                if psutil.swap_memory().percent > 70:
                    succ_sw, msg_sw = self.recycle_swap()
                    results.append(("Reciclagem de Swap", succ_sw, msg_sw))
            except Exception:
                pass

        return results
