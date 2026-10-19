# Graph Report - sysdoctor  (2026-10-19)

## Corpus Check
- 38 files · ~15,433 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 288 nodes · 536 edges · 26 communities (17 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 35 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ebd1801e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]

## God Nodes (most connected - your core abstractions)
1. `run_command()` - 36 edges
2. `BasePackageManager` - 32 edges
3. `command_exists()` - 25 edges
4. `get_available_package_managers()` - 16 edges
5. `AptPackageManager` - 16 edges
6. `SystemMetrics` - 15 edges
7. `report()` - 14 edges
8. `SystemCleaner` - 13 edges
9. `collect_system_metrics()` - 13 edges
10. `DnfPackageManager` - 12 edges

## Surprising Connections (you probably didn't know these)
- `TestAptPackageManager` --uses--> `AptPackageManager`  [INFERRED]
  tests/test_apt.py → sysdoctor/package_managers/apt.py
- `TestPackageManagers` --uses--> `BasePackageManager`  [INFERRED]
  tests/test_package_managers.py → sysdoctor/package_managers/base.py
- `TestSystemCleaner` --uses--> `SystemCleaner`  [INFERRED]
  tests/test_cleaner.py → sysdoctor/core/cleaner.py
- `TestHealthAssessment` --uses--> `SystemMetrics`  [INFERRED]
  tests/test_health.py → sysdoctor/core/system.py
- `TestSystemInspection` --uses--> `SystemMetrics`  [INFERRED]
  tests/test_system.py → sysdoctor/core/system.py

## Import Cycles
- None detected.

## Communities (26 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (25): build_full_report(), Coleta métricas, checa atualizações de pacotes e calcula o Health Score., Converte o relatório em string JSON formatada., report_to_json(), Logger, Path, check_root_privileges(), main() (+17 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (23): DiagnosticItem, evaluate_health(), HealthAssessment, Módulo de cálculo de pontuação de saúde (Health Score) e recomendações., Calcula a pontuação global de saúde (0-100) com base em métricas     de hardware, Módulo de compilação de relatórios e exportação JSON., collect_system_metrics(), detect_linux_distro() (+15 more)

### Community 2 - "Community 2"
Cohesion: 0.26
Nodes (21): analyze_updates(), auto_fix(), bar(), box(), C, clean_snaps(), clear(), detectar_distro() (+13 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (11): ABC, BasePackageManager, Classe base abstrata para gerenciadores de pacotes Linux., Nome legível do gerenciador de pacotes., Verifica se o gerenciador está instalado no sistema., Realiza atualização e limpeza de pacotes pendentes., Limpa caches e arquivos temporários do gerenciador., Gerenciador de pacotes DNF/YUM (Fedora, RHEL, CentOS, Rocky Linux, etc.). (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (14): 1. Menu Interativo (TUI), 2. Linha de Comando (CLI Flags), ⚙️ Automação com Systemd (Timer Diário), 📖 Como Usar, 🤝 Contribuição, 🧪 Executando os Testes Unitários, Exemplos de Uso:, 🚀 Instalação (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.40
Nodes (4): 🛠️ Ações Realizadas, 🎯 Objetivo da Sessão, Relatório de Sessão: Atualização e Sincronização do SysDoctor, 📊 Status Atual

### Community 7 - "Community 7"
Cohesion: 0.18
Nodes (13): Layout, Table, Testes para a interface de monitoramento e dashboard em tempo real., TestDashboard, generate_dashboard_grid(), get_top_processes(), make_layout(), Painel TUI Interativo em Tempo Real utilizando Rich Live. (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (11): 1. Visão Geral e Arquitetura, 2.1 `sysdoctor.core`, 2.2 `sysdoctor.package_managers`, 2.3 `sysdoctor.ui`, 2. Componentes e Módulos Principais, 3.1 CLI, 3.2 Integração Systemd, 3. Interfaces de Execução (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.19
Nodes (8): get_available_package_managers(), Retorna lista com todas as instâncias de gerenciadores disponíveis no sistema., Retorna uma lista de tuplas (nome, revisão) de snaps desativados., SnapPackageManager, BasePackageManager, Any, Testes para detecção e iterabilidade de gerenciadores de pacotes., TestPackageManagers

### Community 10 - "Community 10"
Cohesion: 0.36
Nodes (3): BasePackageManager, FlatpakPackageManager, Any

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (9): get_target_user_home(), Executa auto-correção em todos os gerenciadores de pacotes e no sistema., Retorna o diretório home do usuário real (mesmo se executado com sudo)., Reduz o tamanho dos logs do systemd journald., Limpa miniaturas e caches temporários no ambiente do usuário., Limpa caches de ferramentas de desenvolvimento comuns (uv, pip, npm),         qu, SystemCleaner, Testes para o módulo SystemCleaner e limpezas avançadas de caches. (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.29
Nodes (5): ApkPackageManager, Gerenciador de pacotes APK (Alpine Linux)., Any, Executa um comando de sistema e retorna (code, stdout, stderr)., run_command()

### Community 13 - "Community 13"
Cohesion: 0.27
Nodes (4): AptPackageManager, Retorna a lista de pacotes com status 'rc' (removidos mas com configs residuais), Remove com segurança pacotes em estado 'rc' (configurações residuais),         f, Any

### Community 14 - "Community 14"
Cohesion: 0.31
Nodes (3): Gerenciador de pacotes Zypper (openSUSE)., ZypperPackageManager, Any

### Community 20 - "Community 20"
Cohesion: 0.25
Nodes (5): Gerenciador de pacotes APT (Debian, Ubuntu, Mint, Pop!_OS, etc.)., Gerenciador de pacotes Flatpak., command_exists(), Módulo de execução segura de subprocessos., Verifica se um comando CLI está disponível no PATH.

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (6): 📌 Milestone v2.1.0 — Diagnóstico Avançado de Redes e Containers, 📌 Milestone v2.2.0 — Integração e Observabilidade, 📌 Milestone v2.3.0 — Interface Web Opcional e Histórico de Métricas, 🎯 Próximos Marcos (Milestones), Roadmap do Projeto SysDoctor, 📍 Versão Ativa: v2.0.0 (Lançada / Estável)

### Community 22 - "Community 22"
Cohesion: 0.29
Nodes (6): 1. Versão Ativa & Status Geral de Saúde, 2. Métricas do Smart Gate e Testes Automatizados, 3. Entregas Recentes e Arquivos Modificados, 4. Status dos Deploys e Ambientes, 5. Próximos Passos do Roadmap, Relatório de Atualização de Status: SysDoctor

## Knowledge Gaps
- **33 isolated node(s):** `C`, `Any`, `Any`, `Logger`, `🌟 Principais Recursos` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_available_package_managers()` connect `Community 9` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 23`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `run_command()` connect `Community 12` to `Community 1`, `Community 3`, `Community 4`, `Community 9`, `Community 10`, `Community 11`, `Community 13`, `Community 14`, `Community 20`, `Community 23`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `BasePackageManager` connect `Community 4` to `Community 3`, `Community 9`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 20`, `Community 23`, `Community 25`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `BasePackageManager` (e.g. with `ApkPackageManager` and `AptPackageManager`) actually correct?**
  _`BasePackageManager` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `AptPackageManager` (e.g. with `BasePackageManager` and `BasePackageManager`) actually correct?**
  _`AptPackageManager` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `C`, `SysDoctor - Diagnóstico, monitoramento e manutenção para sistemas Linux.`, `Ponto de entrada do módulo sysdoctor (`python3 -m sysdoctor`).` to the rest of the system?**
  _94 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.10080645161290322 - nodes in this community are weakly interconnected._