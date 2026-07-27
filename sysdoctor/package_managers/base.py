"""
Classe base abstrata para gerenciadores de pacotes Linux.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class BasePackageManager(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome legível do gerenciador de pacotes."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o gerenciador está instalado no sistema."""
        pass

    @abstractmethod
    def check_updates(self) -> Dict[str, Any]:
        """
        Retorna informações sobre atualizações disponíveis:
        {
            "total": int,
            "security": int,
            "phased": bool,
            "details": list[str]
        }
        """
        pass

    @abstractmethod
    def auto_fix(self, dry_run: bool = False) -> Tuple[bool, str]:
        """Realiza atualização e limpeza de pacotes pendentes."""
        pass

    @abstractmethod
    def clean_cache(self, dry_run: bool = False) -> Tuple[bool, str]:
        """Limpa caches e arquivos temporários do gerenciador."""
        pass
