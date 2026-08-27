# Graph Report - sysdoctor  (2026-08-27)

## Corpus Check
- 36 files · ~14,545 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 266 nodes · 497 edges · 18 communities (12 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `919e0c9b`
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
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]

## God Nodes (most connected - your core abstractions)
1. `run_command()` - 34 edges
2. `BasePackageManager` - 32 edges
3. `command_exists()` - 22 edges
4. `get_available_package_managers()` - 16 edges
5. `SystemMetrics` - 15 edges
6. `report()` - 14 edges
7. `collect_system_metrics()` - 13 edges
8. `DnfPackageManager` - 12 edges
9. `SnapPackageManager` - 12 edges
10. `main()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `TestPackageManagers` --uses--> `BasePackageManager`  [INFERRED]
  tests/test_package_managers.py → sysdoctor/package_managers/base.py
- `TestHealthAssessment` --uses--> `SystemMetrics`  [INFERRED]
  tests/test_health.py → sysdoctor/core/system.py
- `TestSystemInspection` --uses--> `SystemMetrics`  [INFERRED]
  tests/test_system.py → sysdoctor/core/system.py
- `Any` --uses--> `BasePackageManager`  [INFERRED]
  sysdoctor/package_managers/dnf.py → sysdoctor/package_managers/base.py
- `Any` --uses--> `BasePackageManager`  [INFERRED]
  sysdoctor/package_managers/flatpak.py → sysdoctor/package_managers/base.py

## Import Cycles
- None detected.

## Communities (18 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (28): Reduz o tamanho dos logs do systemd journald., Limpa miniaturas e caches temporários no ambiente do usuário (se aplicável)., Executa auto-correção em todos os gerenciadores de pacotes e no sistema., SystemCleaner, build_full_report(), Coleta métricas, checa atualizações de pacotes e calcula o Health Score., Converte o relatório em string JSON formatada., report_to_json() (+20 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (23): DiagnosticItem, evaluate_health(), HealthAssessment, Módulo de cálculo de pontuação de saúde (Health Score) e recomendações., Calcula a pontuação global de saúde (0-100) com base em métricas     de hardware, Módulo de compilação de relatórios e exportação JSON., collect_system_metrics(), detect_linux_distro() (+15 more)

### Community 2 - "Community 2"
Cohesion: 0.26
Nodes (21): analyze_updates(), auto_fix(), bar(), box(), C, clean_snaps(), clear(), detectar_distro() (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (8): Módulo de limpeza profunda e auto-correção do sistema., DnfPackageManager, get_available_package_managers(), Retorna lista com todas as instâncias de gerenciadores disponíveis no sistema., Any, BasePackageManager, Testes para detecção e iterabilidade de gerenciadores de pacotes., TestPackageManagers

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (31): ABC, BasePackageManager, ApkPackageManager, Gerenciador de pacotes APK (Alpine Linux)., AptPackageManager, Gerenciador de pacotes APT (Debian, Ubuntu, Mint, Pop!_OS, etc.)., BasePackageManager, Classe base abstrata para gerenciadores de pacotes Linux. (+23 more)

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
Cohesion: 0.39
Nodes (3): Retorna uma lista de tuplas (nome, revisão) de snaps desativados., SnapPackageManager, Any

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (6): 📌 Milestone v2.1.0 — Diagnóstico Avançado de Redes e Containers, 📌 Milestone v2.2.0 — Integração e Observabilidade, 📌 Milestone v2.3.0 — Interface Web Opcional e Histórico de Métricas, 🎯 Próximos Marcos (Milestones), Roadmap do Projeto SysDoctor, 📍 Versão Ativa: v2.0.0 (Lançada / Estável)

### Community 22 - "Community 22"
Cohesion: 0.29
Nodes (6): 1. Versão Ativa & Status Geral de Saúde, 2. Métricas do Smart Gate e Testes Automatizados, 3. Entregas Recentes e Arquivos Modificados, 4. Status dos Deploys e Ambientes, 5. Próximos Passos do Roadmap, Relatório de Atualização de Status: SysDoctor

## Knowledge Gaps
- **33 isolated node(s):** `C`, `Any`, `Any`, `Logger`, `🌟 Principais Recursos` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_command()` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `get_available_package_managers()` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `collect_system_metrics()` connect `Community 1` to `Community 0`, `Community 7`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `BasePackageManager` (e.g. with `ApkPackageManager` and `AptPackageManager`) actually correct?**
  _`BasePackageManager` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SystemMetrics` (e.g. with `DiagnosticItem` and `HealthAssessment`) actually correct?**
  _`SystemMetrics` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `C`, `SysDoctor - Diagnóstico, monitoramento e manutenção para sistemas Linux.`, `Ponto de entrada do módulo sysdoctor (`python3 -m sysdoctor`).` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08232118758434548 - nodes in this community are weakly interconnected._