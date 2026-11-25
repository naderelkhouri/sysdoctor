"""
Módulo de cálculo de pontuação de saúde (Health Score) e recomendações.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from sysdoctor.core.system import SystemMetrics


@dataclass
class DiagnosticItem:
    category: str
    severity: str  # "INFO", "WARNING", "CRITICAL"
    title: str
    message: str
    action_suggestion: str


@dataclass
class HealthAssessment:
    score: int  # 0 to 100
    status_label: str  # "Excelente", "Bom", "Atenção", "Crítico"
    status_color: str  # "green", "yellow", "red"
    items: List[DiagnosticItem] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


def evaluate_health(
    metrics: SystemMetrics, pkg_updates_summary: Dict[str, Any]
) -> HealthAssessment:
    """
    Calcula a pontuação global de saúde (0-100) com base em métricas
    de hardware, serviços falhos, atualizações de segurança e disco.
    """
    score = 100
    items: List[DiagnosticItem] = []
    actions: List[str] = []

    # 1. CPU
    top_cpu = metrics.top_cpu_processes[0] if metrics.top_cpu_processes else None
    cpu_detail = f" Maior consumidor: {top_cpu.name} (PID {top_cpu.pid}, {top_cpu.cpu_percent:.1f}% CPU)." if top_cpu and top_cpu.cpu_percent > 5 else ""

    if metrics.cpu_percent > 90:
        score -= 15
        items.append(
            DiagnosticItem(
                category="CPU",
                severity="CRITICAL",
                title="Processador Sobrecarregado",
                message=f"Uso de CPU muito alto: {metrics.cpu_percent:.1f}%.{cpu_detail}",
                action_suggestion=(
                    f"Considere finalizar {top_cpu.name} (PID {top_cpu.pid}) ou verificar processos via htop."
                    if top_cpu
                    else "Verifique processos com alto consumo usando o monitor ou htop."
                ),
            )
        )
    elif metrics.cpu_percent > 75:
        score -= 5
        items.append(
            DiagnosticItem(
                category="CPU",
                severity="WARNING",
                title="Uso Elevado de CPU",
                message=f"Uso de CPU acima do ideal: {metrics.cpu_percent:.1f}%.{cpu_detail}",
                action_suggestion="Monitore os processos em execução.",
            )
        )

    # 2. Memória RAM
    top_mem = metrics.top_memory_processes[0] if metrics.top_memory_processes else None
    mem_detail = f" Maior consumidor: {top_mem.name} (PID {top_mem.pid}, {top_mem.memory_percent:.1f}% RAM)." if top_mem and top_mem.memory_percent > 5 else ""

    if metrics.memory_percent > 90:
        score -= 15
        items.append(
            DiagnosticItem(
                category="Memória",
                severity="CRITICAL",
                title="Pouca Memória RAM Disponível",
                message=f"Uso de RAM crítico: {metrics.memory_percent:.1f}%.{mem_detail}",
                action_suggestion=(
                    f"Considere fechar {top_mem.name} (PID {top_mem.pid}) para liberar memória."
                    if top_mem
                    else "Encerre aplicações pesadas desnecessárias."
                ),
            )
        )
    elif metrics.memory_percent > 80:
        score -= 5
        items.append(
            DiagnosticItem(
                category="Memória",
                severity="WARNING",
                title="Uso Elevado de Memória RAM",
                message=f"Uso de RAM elevado: {metrics.memory_percent:.1f}%.{mem_detail}",
                action_suggestion="Fique atento ao consumo de memória.",
            )
        )

    # 3. Memória Swap
    top_swap = metrics.top_swap_processes[0] if metrics.top_swap_processes else None
    swap_detail = f" Maior consumidor no Swap: {top_swap.name} (PID {top_swap.pid})." if top_swap and top_swap.swap_bytes > 0 else ""

    if metrics.swap_total_bytes > 0:
        if metrics.swap_percent > 90:
            score -= 10
            items.append(
                DiagnosticItem(
                    category="Swap",
                    severity="CRITICAL",
                    title="Memória Swap Quase Esgotada",
                    message=f"Uso de Swap crítico: {metrics.swap_percent:.1f}%.{swap_detail}",
                    action_suggestion="Considere encerrar processos pesados ou reciclar o swap (swapoff/swapon).",
                )
            )
        elif metrics.swap_percent > 80:
            score -= 5
            items.append(
                DiagnosticItem(
                    category="Swap",
                    severity="WARNING",
                    title="Uso Elevado de Memória Swap",
                    message=f"Uso de Swap elevado: {metrics.swap_percent:.1f}%.{swap_detail}",
                    action_suggestion="Monitore os processos em execução e o uso de memória virtual.",
                )
            )

    # 4. Discos
    for disk in metrics.disks:
        if disk.percent > 90:
            score -= 15
            items.append(
                DiagnosticItem(
                    category="Disco",
                    severity="CRITICAL",
                    title=f"Partição Crítica ({disk.mountpoint})",
                    message=f"Espaço ocupado em {disk.mountpoint}: {disk.percent:.1f}%",
                    action_suggestion=f"Execute auto-correção / limpeza de cache para liberar espaço em {disk.mountpoint}.",
                )
            )
        elif disk.percent > 80:
            score -= 5
            items.append(
                DiagnosticItem(
                    category="Disco",
                    severity="WARNING",
                    title=f"Partição Cheia ({disk.mountpoint})",
                    message=f"Espaço ocupado em {disk.mountpoint}: {disk.percent:.1f}%",
                    action_suggestion=f"Considere apagar arquivos desnecessários em {disk.mountpoint}.",
                )
            )

    # 4. Servicos Systemd Falhos
    if metrics.failed_systemd_units:
        score -= len(metrics.failed_systemd_units) * 10
        units_str = ", ".join(metrics.failed_systemd_units[:3])
        items.append(
            DiagnosticItem(
                category="Serviços",
                severity="CRITICAL",
                title="Serviços Systemd Com Falha",
                message=f"{len(metrics.failed_systemd_units)} serviço(s) falharam: {units_str}",
                action_suggestion="Verifique os logs dos serviços falhos com `systemctl status <servico>`.",
            )
        )

    # 5. Atualizações de Segurança
    sec_count = pkg_updates_summary.get("security", 0)
    total_count = pkg_updates_summary.get("total", 0)

    if sec_count > 0:
        score -= 25
        items.append(
            DiagnosticItem(
                category="Segurança",
                severity="CRITICAL",
                title="Atualizações de Segurança Pendentes",
                message=f"{sec_count} atualização(ões) crítica(s) de segurança pendente(s).",
                action_suggestion="Execute `--fix` ou atualize seus pacotes de segurança imediatamente.",
            )
        )
    elif total_count > 0:
        score -= 10
        items.append(
            DiagnosticItem(
                category="Atualizações",
                severity="WARNING",
                title="Atualizações de Software Pendentes",
                message=f"{total_count} pacote(s) aguardando atualização.",
                action_suggestion="Execute `sysdoctor --fix` para atualizar o sistema.",
            )
        )

    # 6. Reboot necessário
    if metrics.reboot_required:
        score -= 10
        items.append(
            DiagnosticItem(
                category="Sistema",
                severity="WARNING",
                title="Reinicialização Necessária",
                message="O sistema requer reinicialização para aplicar atualizações do kernel/bibliotecas.",
                action_suggestion="Reinicie o sistema assim que conveniente.",
            )
        )

    # 7. Sensores de Temperatura
    if metrics.sensors and metrics.sensors.max_temperature >= 85.0:
        is_crit_temp = metrics.sensors.max_temperature >= 92.0
        score -= 15 if is_crit_temp else 5
        items.append(
            DiagnosticItem(
                category="Hardware",
                severity="CRITICAL" if is_crit_temp else "WARNING",
                title="Temperatura Crítica de Hardware" if is_crit_temp else "Temperatura Elevada de Hardware",
                message=f"Temperatura máxima registrada nos sensores: {metrics.sensors.max_temperature:.1f}°C.",
                action_suggestion="Verifique a saída de ar e ventilação, ou finalize processos que sobrecarregam a CPU/GPU.",
            )
        )

    # 8. Alerta Informativo de Tuning (Swap em disco sem ZRAM)
    if (
        metrics.swap_total_bytes > 0
        and not metrics.zram_active
        and metrics.swap_percent > 85
    ):
        items.append(
            DiagnosticItem(
                category="Tuning",
                severity="WARNING",
                title="Ausência de Compressão de Memória (ZRAM)",
                message="Swap em disco saturado sem módulo de compressão ZRAM/Zswap ativo.",
                action_suggestion="Recomenda-se habilitar ZRAM (pacote zram-tools) para reduzir gargalos de I/O em disco.",
            )
        )

    score = max(0, min(100, score))

    # Determina o rótulo e a cor
    if score >= 90:
        status_label = "Excelente"
        status_color = "green"
    elif score >= 70:
        status_label = "Bom"
        status_color = "green"
    elif score >= 50:
        status_label = "Atenção"
        status_color = "yellow"
    else:
        status_label = "Crítico"
        status_color = "red"

    # Ações recomendadas priorizadas
    for item in items:
        if item.severity == "CRITICAL":
            actions.append(f"[CRÍTICO] {item.action_suggestion}")
    for item in items:
        if item.severity == "WARNING":
            actions.append(f"[AVISO] {item.action_suggestion}")

    if not actions:
        actions.append("Nenhuma ação urgente necessária. Sistema operando em perfeito estado.")

    return HealthAssessment(
        score=score,
        status_label=status_label,
        status_color=status_color,
        items=items,
        recommended_actions=actions,
    )
