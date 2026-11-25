"""
Módulo de inspeção de hardware, sistema operacional e métricas.
"""

import os
import sys
import platform
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from sysdoctor.utils.runner import command_exists, run_command


@dataclass
class ProcessMetric:
    pid: int
    name: str
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_rss_bytes: int = 0
    swap_bytes: int = 0


@dataclass
class HardwareSensors:
    temperatures: Dict[str, float] = field(default_factory=dict)
    max_temperature: float = 0.0
    battery_percent: Optional[float] = None
    battery_plugged: Optional[bool] = None


@dataclass
class DiskHogInfo:
    path: str
    size_bytes: int
    human_size: str


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
    top_cpu_processes: List[ProcessMetric] = field(default_factory=list)
    top_memory_processes: List[ProcessMetric] = field(default_factory=list)
    top_swap_processes: List[ProcessMetric] = field(default_factory=list)
    sensors: Optional[HardwareSensors] = None
    zram_active: bool = False
    swappiness: Optional[int] = None
    disk_hogs: List[DiskHogInfo] = field(default_factory=list)


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


def _get_process_swap_bytes(pid: int) -> int:
    """Extrai o tamanho de VmSwap em bytes de /proc/[pid]/status."""
    try:
        status_path = f"/proc/{pid}/status"
        if not os.path.exists(status_path):
            return 0
        with open(status_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("VmSwap:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return int(parts[1]) * 1024
    except Exception:
        pass
    return 0


def get_top_processes(
    count: int = 5,
) -> Tuple[List[ProcessMetric], List[ProcessMetric], List[ProcessMetric]]:
    """
    Coleta e retorna tupla com (top_cpu, top_memory, top_swap) ProcessMetrics.
    """
    procs: List[ProcessMetric] = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            p_info = p.info
            pid = p_info["pid"]
            name = p_info["name"] or "desconhecido"
            cpu_p = float(p_info.get("cpu_percent") or 0.0)
            mem_p = float(p_info.get("memory_percent") or 0.0)
            try:
                rss = p.memory_info().rss
            except Exception:
                rss = 0
            swap_b = _get_process_swap_bytes(pid)

            procs.append(
                ProcessMetric(
                    pid=pid,
                    name=name,
                    cpu_percent=cpu_p,
                    memory_percent=mem_p,
                    memory_rss_bytes=rss,
                    swap_bytes=swap_b,
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, ProcessLookupError):
            continue
        except Exception:
            continue

    top_cpu = sorted(procs, key=lambda x: x.cpu_percent, reverse=True)[:count]
    top_memory = sorted(procs, key=lambda x: x.memory_percent, reverse=True)[:count]
    top_swap = sorted(
        [p for p in procs if p.swap_bytes > 0],
        key=lambda x: x.swap_bytes,
        reverse=True,
    )[:count]

    return top_cpu, top_memory, top_swap


def collect_hardware_sensors() -> HardwareSensors:
    """Coleta temperaturas de sensores de hardware e status da bateria."""
    temps: Dict[str, float] = {}
    max_t = 0.0

    if hasattr(psutil, "sensors_temperatures"):
        try:
            raw_temps = psutil.sensors_temperatures() or {}
            for chip, entries in raw_temps.items():
                for entry in entries:
                    if entry.current is not None and entry.current > 0:
                        lbl = f"{chip} {entry.label}".strip()
                        temps[lbl] = float(entry.current)
                        if entry.current > max_t:
                            max_t = float(entry.current)
        except Exception:
            pass

    bat_percent: Optional[float] = None
    bat_plugged: Optional[bool] = None
    if hasattr(psutil, "sensors_battery"):
        try:
            bat = psutil.sensors_battery()
            if bat:
                bat_percent = float(bat.percent)
                bat_plugged = bool(bat.power_plugged)
        except Exception:
            pass

    return HardwareSensors(
        temperatures=temps,
        max_temperature=max_t,
        battery_percent=bat_percent,
        battery_plugged=bat_plugged,
    )


def get_kernel_tuning_info() -> Tuple[bool, Optional[int]]:
    """Verifica se zram está ativo e obtém o valor de vm.swappiness."""
    zram_active = False
    try:
        if os.path.exists("/dev/zram0"):
            zram_active = True
        elif os.path.exists("/proc/swaps"):
            with open("/proc/swaps", "r", encoding="utf-8", errors="ignore") as f:
                if "zram" in f.read().lower():
                    zram_active = True
    except Exception:
        pass

    swappiness: Optional[int] = None
    try:
        if os.path.exists("/proc/sys/vm/swappiness"):
            with open("/proc/sys/vm/swappiness", "r", encoding="utf-8") as f:
                swappiness = int(f.read().strip())
    except Exception:
        pass

    return zram_active, swappiness


def _format_bytes(bytes_val: int) -> str:
    """Formata bytes em string humanamente legível (MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0 or unit == "TB":
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} GB"


def inspect_disk_hogs() -> List[DiskHogInfo]:
    """Identifica diretórios conhecidos de alto consumo de armazenamento."""
    candidate_paths = [
        "/var/lib/snapd",
        "/var/log",
        "/var/crash",
        "/var/cache",
        "/var/lib/docker",
    ]
    # Adiciona cache de usuário atual ou SUDO_USER
    sudo_user = os.environ.get("SUDO_USER")
    home_dir = os.path.expanduser(f"~{sudo_user}") if sudo_user else os.path.expanduser("~")
    user_cache = os.path.join(home_dir, ".cache")
    if os.path.exists(user_cache):
        candidate_paths.append(user_cache)

    hogs: List[DiskHogInfo] = []
    for path in candidate_paths:
        if not os.path.exists(path):
            continue
        try:
            # Executa 'du -sb' com timeout curto de 2s para evitar travas em discos lentos
            code, out, _ = run_command(["du", "-sb", path], timeout=3)
            if code == 0 and out:
                size_str = out.split()[0]
                size_b = int(size_str)
                # Só lista diretórios com mais de 50MB
                if size_b >= 50 * 1024 * 1024:
                    hogs.append(
                        DiskHogInfo(
                            path=path,
                            size_bytes=size_b,
                            human_size=_format_bytes(size_b),
                        )
                    )
        except Exception:
            continue

    hogs.sort(key=lambda x: x.size_bytes, reverse=True)
    return hogs


def collect_system_metrics(lightweight: bool = False) -> SystemMetrics:
    """
    Coleta todas as estatísticas atuais do sistema.
    Se lightweight=True (ex: TUI Live Monitor), omite varreduras pesadas de disco (du -sb),
    systemctl --failed e iteração duplicada de processos.
    """
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

    sensors = collect_hardware_sensors()
    if lightweight:
        top_cpu, top_mem, top_swap = [], [], []
        zram_active, swappiness = False, None
        disk_hogs = []
        failed_units = []
        cpu_pct = psutil.cpu_percent(interval=None)
    else:
        top_cpu, top_mem, top_swap = get_top_processes(count=5)
        zram_active, swappiness = get_kernel_tuning_info()
        disk_hogs = inspect_disk_hogs()
        failed_units = get_failed_systemd_units()
        cpu_pct = psutil.cpu_percent(interval=0.5)

    return SystemMetrics(
        os_name=detect_linux_distro(),
        kernel_version=platform.release(),
        architecture=platform.machine(),
        hostname=platform.node(),
        uptime_seconds=uptime,
        cpu_percent=cpu_pct,
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
        failed_systemd_units=failed_units,
        reboot_required=is_reboot_required(),
        top_cpu_processes=top_cpu,
        top_memory_processes=top_mem,
        top_swap_processes=top_swap,
        sensors=sensors,
        zram_active=zram_active,
        swappiness=swappiness,
        disk_hogs=disk_hogs,
    )
