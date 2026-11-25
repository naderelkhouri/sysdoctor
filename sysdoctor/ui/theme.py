"""
Design System, Paleta de Cores e Componentes Visuais do SysDoctor.
"""

from rich.theme import Theme
from rich.console import Console
from rich import box

# ── Paleta de Cores Semântica (TrueColor / Modern Dark Theme) ──────
COLOR_PRIMARY = "#06b6d4"       # Cyan vibrante
COLOR_PRIMARY_LIGHT = "#22d3ee" # Cyan claro
COLOR_SECONDARY = "#818cf8"     # Indigo suave
COLOR_PURPLE = "#a855f7"        # Púrpura moderno
COLOR_SUCCESS = "#10b981"       # Esmeralda / Seguro
COLOR_SUCCESS_BG = "#064e3b"    # Fundo escuro de sucesso
COLOR_WARNING = "#f59e0b"       # Âmbar / Atenção
COLOR_WARNING_BG = "#78350f"    # Fundo escuro de aviso
COLOR_DANGER = "#ef4444"        # Rosa / Vermelho Crítico
COLOR_DANGER_BG = "#7f1d1d"     # Fundo escuro crítico
COLOR_MUTED = "#64748b"         # Cinza ardósia suave
COLOR_BORDER = "#334155"        # Bordas de cartões
COLOR_BORDER_FOCUS = "#38bdf8"  # Borda ativa
COLOR_TEXT = "#f8fafc"          # Texto principal de alto contraste
COLOR_TEXT_DIM = "#94a3b8"      # Texto secundário

# Estilo padrão de caixas para cartões do design system
CARD_BOX = box.ROUNDED
TABLE_BOX = box.SIMPLE_HEAD

SYSDOCTOR_THEME = Theme(
    {
        "info": f"bold {COLOR_PRIMARY_LIGHT}",
        "primary": COLOR_PRIMARY,
        "secondary": COLOR_SECONDARY,
        "accent": COLOR_PURPLE,
        "warning": f"bold {COLOR_WARNING}",
        "critical": f"bold {COLOR_DANGER}",
        "success": f"bold {COLOR_SUCCESS}",
        "score_good": f"bold {COLOR_SUCCESS}",
        "score_warn": f"bold {COLOR_WARNING}",
        "score_bad": f"bold {COLOR_DANGER}",
        "header": f"bold {COLOR_PRIMARY_LIGHT}",
        "muted": COLOR_TEXT_DIM,
        "border": COLOR_BORDER,
        "text": COLOR_TEXT,
    }
)

console = Console(theme=SYSDOCTOR_THEME)


def make_badge(text: str, level: str = "info") -> str:
    """Gera uma pílula (badge) de alto contraste visual."""
    level = level.upper()
    if level in ("CRITICAL", "DANGER", "RED", "ERROR"):
        return f"[bold white on #dc2626]  ✖ {text}  [/]"
    elif level in ("WARNING", "WARN", "YELLOW", "ATENÇÃO"):
        return f"[bold black on #f59e0b]  ▲ {text}  [/]"
    elif level in ("SUCCESS", "OK", "GREEN", "BOM", "EXCELENTE"):
        return f"[bold white on #059669]  ● {text}  [/]"
    elif level in ("PRIMARY", "CYAN"):
        return f"[bold white on #0284c7]  ◈ {text}  [/]"
    elif level in ("PURPLE", "MAGENTA"):
        return f"[bold white on #7c3aed]  ◆ {text}  [/]"
    return f"[bold white on #475569]  ℹ {text}  [/]"


def render_gauge(percent: float, width: int = 22, show_badge: bool = True) -> str:
    """
    Renderiza barra visual de progresso proporcional e estilizada
    utilizando blocos segmentados e paleta gradiente.
    """
    percent = max(0.0, min(100.0, float(percent)))
    filled = int(round(width * percent / 100.0))
    empty = max(0, width - filled)

    if percent < 70.0:
        bar_color = COLOR_SUCCESS
        badge_text = f"[bold {COLOR_SUCCESS}]{percent:5.1f}%[/]"
    elif percent < 85.0:
        bar_color = COLOR_WARNING
        badge_text = f"[bold {COLOR_WARNING}]{percent:5.1f}%[/]"
    else:
        bar_color = COLOR_DANGER
        badge_text = f"[bold {COLOR_DANGER}]{percent:5.1f}%[/]"

    fill_str = f"[{bar_color}]{'▰' * filled}[/]"
    empty_str = f"[{COLOR_BORDER}]{'▱' * empty}[/]"

    if show_badge:
        return f"{fill_str}{empty_str} {badge_text}"
    return f"{fill_str}{empty_str}"


def format_bytes_human(bytes_val: int) -> str:
    """Converte bytes para formato legível (KB, MB, GB)."""
    val = float(bytes_val)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if val < 1024.0 or unit == "TB":
            return f"{val:.1f} {unit}"
        val /= 1024.0
    return f"{val:.1f} GB"
