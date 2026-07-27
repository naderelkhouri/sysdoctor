#!/usr/bin/env python3
"""
SysDoctor - Multi-Distro Linux Health & Maintenance Tool.
Backward compatibility wrapper for sysdoctor package.
"""

import sys
import os

# Adiciona o diretório atual ao sys.path para garantir que o pacote local seja encontrado
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from sysdoctor.cli import main
except ImportError as e:
    print(f"Erro ao carregar o pacote SysDoctor: {e}")
    print("Certifique-se de que psutil e rich estão instalados:")
    print("  pip install psutil rich")
    sys.exit(1)

if __name__ == "__main__":
    main()