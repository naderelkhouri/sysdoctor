"""
Módulo de execução segura de subprocessos.
"""

import subprocess
import shutil
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger("sysdoctor")


def command_exists(cmd: str) -> bool:
    """Verifica se um comando CLI está disponível no PATH."""
    return shutil.which(cmd) is not None


def run_command(
    cmd: List[str],
    timeout: int = 120,
    check: bool = False,
    env: Optional[dict] = None,
    dry_run: bool = False,
) -> Tuple[int, str, str]:
    """Executa um comando de sistema e retorna (code, stdout, stderr)."""
    if dry_run:
        logger.info(f"[DRY-RUN] Executando: {' '.join(cmd)}")
        return 0, "[DRY-RUN] Comando simulado com sucesso.", ""

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env=env,
        )
        if check and proc.returncode != 0:
            logger.error(f"Comando falhou com código {proc.returncode}: {' '.join(cmd)}")
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Comando excedeu o tempo limite ({timeout}s): {' '.join(cmd)}")
        return 124, "", "Timeout na execução do comando."
    except Exception as e:
        logger.error(f"Erro ao executar {' '.join(cmd)}: {e}")
        return 1, "", str(e)
