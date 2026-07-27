# 🩺 SysDoctor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-Linux-orange.svg)](https://www.kernel.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

**SysDoctor** é uma ferramenta profissional (CLI & TUI em tempo real) para **diagnóstico de saúde, monitoramento e manutenção automatizada** em distribuições Linux.

Criado para administradores de sistemas, engenheiros de DevOps e entusiastas do ecossistema Linux, o SysDoctor oferece relatórios visuais com Rich, cálculo ponderado de *Health Score*, e suporte nativo a múltiplos gerenciadores de pacotes.

---

```
  🩺 SysDoctor v2.0.0 — Diagnóstico & Manutenção Linux
  ╔═════════════════════════════════════════════════════╗
  ║ 1 🩺 Relatório Completo de Saúde                    ║
  ║ 2 🔧 Auto-Correção e Limpeza do Sistema             ║
  ║ 3 📊 Monitor em Tempo Real (Live TUI)               ║
  ║ 4 📄 Exportar Relatório em JSON                     ║
  ║ 0 🚪 Sair                                           ║
  ╚═════════════════════════════════════════════════════╝
```

---

## 🌟 Principais Recursos

- **🩺 Health Score Ponderado (0-100)**: Avalia o estado geral do sistema analisando carga de CPU, consumo de RAM/Swap, espaço em disco, pacotes vulneráveis de segurança e unidades `systemd` com falhas.
- **📦 Suporte Multi-Distro Extensível**:
  - **APT**: Debian, Ubuntu, Linux Mint, Pop!_OS, Zorin OS
  - **DNF/YUM**: Fedora, RHEL, CentOS, Rocky Linux, AlmaLinux
  - **Pacman**: Arch Linux, Manjaro, EndeavourOS (com verificação de órfãos)
  - **Zypper**: openSUSE
  - **APK**: Alpine Linux
  - **Universal**: Snap (com limpeza de revisões antigas/desativadas) & Flatpak (com remoção de runtimes inutilizadas)
- **📊 Monitor em Tempo Real (TUI)**: Interface interativa alimentada por `rich.live` com progresso visual de hardware, uso de partições e top processos por consumo de CPU/RAM.
- **🧹 Limpeza Profunda & Auto-Correção**:
  - Atualizações automáticas seguras de pacotes
  - Remoção de pacotes órfãos e desnecessários
  - Truncamento inteligente de logs do `journalctl` (`--vacuum-size=100M`)
  - Limpeza de caches de pacotes e miniaturas
- **🤖 Scriptável & Pronto para Automação**: Exportação dos dados diagnósticos em formato **JSON** para integração com Zabbix, Prometheus, Datadog ou scripts CI/CD.

---

## 🚀 Instalação

### Pré-requisitos
- Python **3.8+**
- Permissões de superusuário (`sudo`) para tarefas de manutenção.

### Método 1: Clonar e Instalar Localmente (Recomendado)
```bash
git clone https://github.com/naderelkhouri/sysdoctor.git
cd sysdoctor
pip install -e .
```

### Método 2: Instalação rápida de dependências e execução direta
```bash
pip install psutil rich
python3 -m sysdoctor
```

---

## 📖 Como Usar

### 1. Menu Interativo (TUI)
Basta executar `sysdoctor` ou `sudo sysdoctor` sem argumentos:
```bash
sysdoctor
```

### 2. Linha de Comando (CLI Flags)

| Flag | Descrição |
| --- | --- |
| `-r`, `--report` | Gera e exibe um relatório completo de saúde no terminal. |
| `-f`, `--fix` | Executa a auto-correção e limpeza completa do sistema (`sudo` recomendado). |
| `-m`, `--monitor` | Abre a interface de monitoramento interativo em tempo real. |
| `-j`, `--json` | Retorna o relatório em JSON para pipelines ou ferramentas de monitoramento. |
| `--dry-run` | Simula a execução sem aplicar alterações reais no sistema. |
| `-v`, `--version` | Exibe a versão instalada. |

#### Exemplos de Uso:

**Gerar Relatório Rápido:**
```bash
sysdoctor --report
```

**Executar Auto-Correção em Modo de Simulação (Dry-Run):**
```bash
sysdoctor --fix --dry-run
```

**Exportar Métrica de Saúde para Scripting:**
```bash
sysdoctor --json | jq .health.score
```

---

## ⚙️ Automação com Systemd (Timer Diário)

Para agendar a manutenção diária automática do seu servidor/desktop:

```bash
sudo cp extra/sysdoctor.service /etc/systemd/system/
sudo cp extra/sysdoctor.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sysdoctor.timer
```

---

## 🧪 Executando os Testes Unitários

O SysDoctor possui uma suíte de testes unitários integrada:

```bash
python3 -m unittest discover -s tests
```

---

## 🤝 Contribuição

Contribuições da comunidade Linux são super vindas!
1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/minha-nova-feature`)
3. Commit suas alterações (`git commit -m 'feat: adiciona suporte a novo gerenciador'`)
4. Faça o Push para a Branch (`git push origin feature/minha-nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja [`LICENSE`](LICENSE) para mais detalhes.

Desenvolvido por **Nader El Khouri** com apoio da comunidade Linux. 🐧
