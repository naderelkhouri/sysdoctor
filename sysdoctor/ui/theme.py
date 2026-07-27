"""
Tema e estilos visuais para Rich.
"""

from rich.theme import Theme
from rich.console import Console

SYSDOCTOR_THEME = Theme(
    {
        "info": "cyan",
        "warning": "bold yellow",
        "critical": "bold red",
        "success": "bold green",
        "score_good": "bold green",
        "score_warn": "bold yellow",
        "score_bad": "bold red",
        "header": "bold cyan",
        "muted": "dim white",
    }
)

console = Console(theme=SYSDOCTOR_THEME)
