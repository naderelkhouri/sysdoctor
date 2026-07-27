"""
Módulo de compilação de relatórios e exportação JSON.
"""

import json
import datetime
from typing import Dict, Any
from sysdoctor.core.system import collect_system_metrics, SystemMetrics
from sysdoctor.core.health import evaluate_health, HealthAssessment
from sysdoctor.package_managers import get_available_package_managers


def build_full_report() -> Dict[str, Any]:
    """Coleta métricas, checa atualizações de pacotes e calcula o Health Score."""
    metrics: SystemMetrics = collect_system_metrics()

    # Checa pacotes em todos os gerenciadores ativos
    managers = get_available_package_managers()
    pkg_summary = {"total": 0, "security": 0, "phased": False, "managers": {}}

    for mgr in managers:
        info = mgr.check_updates()
        pkg_summary["total"] += info.get("total", 0)
        pkg_summary["security"] += info.get("security", 0)
        if info.get("phased"):
            pkg_summary["phased"] = True
        pkg_summary["managers"][mgr.name] = info

    assessment: HealthAssessment = evaluate_health(metrics, pkg_summary)

    report_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system": {
            "os_name": metrics.os_name,
            "kernel": metrics.kernel_version,
            "architecture": metrics.architecture,
            "hostname": metrics.hostname,
            "uptime_seconds": metrics.uptime_seconds,
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "swap_percent": metrics.swap_percent,
            "disks": [
                {
                    "mountpoint": d.mountpoint,
                    "device": d.device,
                    "percent": d.percent,
                    "total_bytes": d.total_bytes,
                    "free_bytes": d.free_bytes,
                }
                for d in metrics.disks
            ],
            "failed_systemd_units": metrics.failed_systemd_units,
            "reboot_required": metrics.reboot_required,
        },
        "packages": pkg_summary,
        "health": {
            "score": assessment.score,
            "status_label": assessment.status_label,
            "status_color": assessment.status_color,
            "items": [
                {
                    "category": item.category,
                    "severity": item.severity,
                    "title": item.title,
                    "message": item.message,
                    "action": item.action_suggestion,
                }
                for item in assessment.items
            ],
            "recommended_actions": assessment.recommended_actions,
        },
    }

    return report_data


def report_to_json(report_dict: Dict[str, Any], indent: int = 2) -> str:
    """Converte o relatório em string JSON formatada."""
    return json.dumps(report_dict, indent=indent, ensure_ascii=False)
