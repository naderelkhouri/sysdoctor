# Especificação Técnica (SPEC): SysDoctor v2.0.0

- **Projeto:** SysDoctor
- **Versão:** 2.0.0
- **Status:** Produção / Estável
- **Autor:** Nader El Khouri
- **Data:** 27 de Agosto de 2026

---

## 1. Visão Geral e Arquitetura

O **SysDoctor** é uma suíte unificada para diagnóstico, monitoramento em tempo real e manutenção automatizada de distribuições Linux. Desenvolvido em Python 3 modular, integra bibliotecas de alto desempenho (`psutil`, `rich`) e abstrações para múltiplos gerenciadores de pacotes de sistemas Linux e formatos universais (Snap, Flatpak).

### Diagrama de Camadas da Arquitetura

```
┌────────────────────────────────────────────────────────┐
│                   Entrada do Usuário                  │
│       CLI Flags (`sysdoctor -r|-f|-m|-j`) / TUI        │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│                    sysdoctor.cli                       │
│        (Orquestrador de Execução e Modos)              │
└────────┬─────────────────┬───────────────────┬─────────┘
         │                 │                   │
┌────────▼─────────┐┌──────▼──────────┐┌───────▼─────────┐
│ sysdoctor.core   ││ sysdoctor.ui    ││package_managers │
│ - health.py      ││ - dashboard.py  ││ - apt, dnf, apk │
│ - system.py      ││ - theme.py      ││ - pacman, zypper│
│ - cleaner.py     ││ - views.py      ││ - snap, flatpak │
│ - reporter.py    │└─────────────────┘└─────────────────┘
└──────────────────┘
```

---

## 2. Componentes e Módulos Principais

### 2.1 `sysdoctor.core`
- **`system.py`**: Coleta dados de telemetria de hardware e SO através de `psutil` e inspeção de `/proc`, `/sys` e `systemd`.
  - CPU (uso total, por núcleo, load average).
  - Memória RAM e Swap.
  - Partições de disco (pontos de montagem, espaço total/usado/livre, inodes).
  - Unidades Systemd em estado de falha (`systemctl --failed`).
- **`health.py`**: Algoritmo ponderado de cálculo do **Health Score (0 a 100)**:
  - CPU > 85% (-15 pts), CPU > 95% (-25 pts).
  - RAM > 90% (-20 pts).
  - Swap > 70% (-15 pts).
  - Partições de disco > 85% (-20 pts por partição crítica).
  - Unidades Systemd falhas (-10 pts por serviço falho).
  - Atualizações de segurança pendentes (-15 pts).
- **`cleaner.py`**: Motor de manutenção e auto-correção:
  - Atualização automatizada de repositórios e pacotes.
  - Remoção de pacotes órfãos e desnecessários (`autoremove` / `orphans`).
  - Limpeza de logs do `journalctl` com retenção limite configurada (`--vacuum-size=100M`).
  - Limpeza de caches de pacotes e thumbnails de usuários.
  - Suporte a modo `--dry-run` para auditoria sem mutações.
- **`reporter.py`**: Estruturação de relatórios em memória e conversão para JSON serializável.

### 2.2 `sysdoctor.package_managers`
Abstração polimórfica via classe base `PackageManagerBase`:
- `detect()`: Verifica se o gerenciador está instalado no sistema.
- `check_updates()`: Retorna lista de pacotes atualizáveis e sinaliza atualizações de segurança.
- `update_all()`: Executa rotina de upgrade.
- `clean()`: Limpa caches e pacotes obsoletos.

Implementações nativas suportadas:
1. `AptManager` (Debian, Ubuntu, Linux Mint, Pop!_OS)
2. `DnfManager` (Fedora, RHEL, CentOS, Rocky Linux)
3. `PacmanManager` (Arch Linux, Manjaro, EndeavourOS)
4. `ZypperManager` (openSUSE)
5. `ApkManager` (Alpine Linux)
6. `SnapManager` (Universal Snap packages)
7. `FlatpakManager` (Universal Flatpak runtimes & apps)

### 2.3 `sysdoctor.ui`
- **`views.py`**: Renderização estática com tabelas e painéis `rich` elegantes para o modo `--report`.
- **`dashboard.py`**: Monitor TUI interativo em tempo real via `rich.live.Live`, exibindo métricas dinâmicas a cada 1s.
- **`theme.py`**: Definições de cores e estilos corporativos consistentes.

---

## 3. Interfaces de Execução

### 3.1 CLI
```bash
sysdoctor [opções]
  -h, --help            Exibe ajuda e opções
  -v, --version         Exibe a versão instalada (2.0.0)
  -r, --report          Exibe relatório estático de saúde
  -f, --fix             Executa auto-correção e limpeza
  -m, --monitor         Inicia TUI de monitoramento em tempo real
  -j, --json            Gera saída estruturada em JSON
  --dry-run             Simula sem efetuar alterações
  --verbose             Logs detalhados
  -y, --yes             Confirmação automática de prompts
```

### 3.2 Integração Systemd
- `extra/sysdoctor.service`: Unidade OneShot para execução de auto-manutenção.
- `extra/sysdoctor.timer`: Disparador agendado diário (ex: 03:00 AM).

---

## 4. Requisitos de Qualidade e Testes
- Suíte de testes unitários em `tests/` com cobertura dos módulos centrais (`test_health.py`, `test_system.py`, `test_package_managers.py`).
- Compatibilidade validada com Python 3.8 até 3.14.
