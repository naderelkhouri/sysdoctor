"""
Módulo de logging para o SysDoctor.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logger(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("sysdoctor")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if logger.handlers:
        return logger

    # Console Handler
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG if verbose else logging.WARNING)
    formatter = logging.formatters = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler if root or user writable path exists
    try:
        log_dir = Path("/var/log/sysdoctor") if os.geteuid() == 0 else Path.home() / ".local/state/sysdoctor"
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_dir / "sysdoctor.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass

    return logger
