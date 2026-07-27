"""
Módulo inicializador e detector de Gerenciadores de Pacotes.
"""

from typing import List
from sysdoctor.package_managers.base import BasePackageManager
from sysdoctor.package_managers.apt import AptPackageManager
from sysdoctor.package_managers.dnf import DnfPackageManager
from sysdoctor.package_managers.pacman import PacmanPackageManager
from sysdoctor.package_managers.zypper import ZypperPackageManager
from sysdoctor.package_managers.apk import ApkPackageManager
from sysdoctor.package_managers.snap import SnapPackageManager
from sysdoctor.package_managers.flatpak import FlatpakPackageManager


def get_available_package_managers() -> List[BasePackageManager]:
    """Retorna lista com todas as instâncias de gerenciadores disponíveis no sistema."""
    all_managers = [
        AptPackageManager(),
        DnfPackageManager(),
        PacmanPackageManager(),
        ZypperPackageManager(),
        ApkPackageManager(),
        SnapPackageManager(),
        FlatpakPackageManager(),
    ]
    return [pm for pm in all_managers if pm.is_available()]
