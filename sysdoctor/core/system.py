"""
Módulo de inspeção de hardware, sistema operacional e métricas.
"""

import os
import sys
import platform
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Any
from sysdoctor.utils.runner import command_exists, run_command


@dataclass
class DiskPartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


@dataclass
class SystemMetrics:
    os_name: str
    kernel_version: str
    architecture: str
    hostname: str
    uptime_seconds: float
    cpu_percent: float
    cpu_count_logical: int
    cpu_count_physical: int
    memory_percent: float
    memory_total_bytes: int
    memory_used_bytes: int
    memory_available_bytes: int
    swap_percent: float
    swap_total_bytes: int
    swap_used_bytes: int
    disks: List[DiskPartitionInfo] = field(default_factory=list)
    failed_systemd_units: List[str] = field(default_factory=list)
    reboot_required: bool = False


def detect_linux_distro() -> str:
    """Detecta o nome e versão da distribuição Linux."""
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                data = {}
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        data[k] = v.strip('"')
                if "PRETTY_NAME" in data:
                    return data["PRETTY_NAME"]
                elif "NAME" in data:
                    return data["NAME"]
    except Exception:
        pass
    return f"Linux {platform.release()}"


def is_reboot_required() -> bool:
    """Verifica se uma reinicialização é necessária."""
    if os.path.exists("/var/run/reboot-required"):
        return True
    if os.path.exists("/var/run/reboot-required.pkgs"):
        return True
    return False


def get_failed_systemd_units() -> List[str]:
    """Retorna lista de unidades systemd com estado 'failed'."""
    if not command_exists("systemctl"):
        return []
    code, out, _ = run_command(["systemctl", "--failed", "--no-legend", "--plain"], timeout=10)
    if code == 0 and out:
        units = []
        for line in out.splitlines():
            parts = line.split()
            if parts:
                units.append(parts[0])
        return units
    return []


def collect_system_metrics() -> SystemMetrics:
    """Coleta todas as estatísticas atuais do sistema."""
    boot_time = psutil.boot_time()
    uptime = float(psutil.time.time() - boot_time)

    # Memória
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Discos
    ignore_fstypes = {"tmpfs", "squashfs", "devtmpfs", "overlay", "iso9660"}
    ignore_mounts = {"/snap", "/run", "/proc", "/sys", "/dev"}

    disks_info = []
    for part in psutil.disk_partitions(all=False):
        if part.fstype.lower() in ignore_fstypes:
            continue
        if any(part.mountpoint.startswith(ign) for ign in ignore_mounts if ign != "/"):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks_info.append(
                DiskPartitionInfo(
                    device=part.device,
                    mountpoint=part.mountpoint,
                    fstype=part.fstype,
                    total_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free,
                    percent=usage.percent,
                )
            )
        except PermissionError:
            continue
        except Exception:
            continue

    return SystemMetrics(
        os_name=detect_linux_distro(),
        kernel_version=platform.release(),
        architecture=platform.machine(),
        hostname=platform.node(),
        uptime_seconds=uptime,
        cpu_percent=psutil.cpu_percent(interval=0.5),
        cpu_count_logical=psutil.cpu_count(logical=True) or 1,
        cpu_count_physical=psutil.cpu_count(logical=False) or 1,
        memory_percent=mem.percent,
        memory_total_bytes=mem.total,
        memory_used_bytes=mem.used,
        memory_available_bytes=mem.available,
        swap_percent=swap.percent,
        swap_total_bytes=swap.total,
        swap_used_bytes=swap.used,
        disks=disks_info,
        failed_systemd_units=get_failed_systemd_units(),
        reboot_required=is_reboot_required(),
    )
