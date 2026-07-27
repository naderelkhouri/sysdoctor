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
    if metrics.cpu_percent > 90:
        score -= 15
        items.append(
            DiagnosticItem(
                category="CPU",
                severity="CRITICAL",
                title="Processador Sobrecarregado",
                message=f"Uso de CPU muito alto: {metrics.cpu_percent:.1f}%",
                action_suggestion="Verifique processos com alto consumo usando o monitor ou htop.",
            )
        )
    elif metrics.cpu_percent > 75:
        score -= 5
        items.append(
            DiagnosticItem(
                category="CPU",
                severity="WARNING",
                title="Uso Elevado de CPU",
                message=f"Uso de CPU acima do ideal: {metrics.cpu_percent:.1f}%",
                action_suggestion="Monitore os processos em execução.",
            )
        )

    # 2. Memória RAM
    if metrics.memory_percent > 90:
        score -= 15
        items.append(
            DiagnosticItem(
                category="Memória",
                severity="CRITICAL",
                title="Pouca Memória RAM Disponível",
                message=f"Uso de RAM crítico: {metrics.memory_percent:.1f}%",
                action_suggestion="Encerre aplicações pesadas desnecessárias.",
            )
        )
    elif metrics.memory_percent > 80:
        score -= 5
        items.append(
            DiagnosticItem(
                category="Memória",
                severity="WARNING",
                title="Uso Elevado de Memória RAM",
                message=f"Uso de RAM elevado: {metrics.memory_percent:.1f}%",
                action_suggestion="Fique atento ao consumo de memória.",
            )
        )

    # 3. Discos
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
