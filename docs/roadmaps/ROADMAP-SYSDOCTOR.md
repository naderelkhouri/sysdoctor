# Roadmap do Projeto SysDoctor

Este documento delineia o ciclo de vida, marcos evolutivos e planos de melhoria contínua para o **SysDoctor**.

---

## 📍 Versão Ativa: v2.0.0 (Lançada / Estável)
- [x] Arquitetura modular desacoplada (`core`, `package_managers`, `ui`, `utils`).
- [x] Suporte multi-distro polimórfico (APT, DNF, Pacman, Zypper, APK, Snap, Flatpak).
- [x] Cálculo ponderado de Health Score (0-100).
- [x] Interface rica no terminal com Rich (relatório estático e Live TUI).
- [x] Exportação de diagnóstico estruturado em formato JSON (`sysdoctor --json`).
- [x] Automação com Systemd (service & timer).
- [x] Suíte de testes unitários automatizados (100% aprovados).
- [x] Wrapper executável global em `~/.local/bin/sysdoctor` e atalho de desktop.

---

## 🎯 Próximos Marcos (Milestones)

### 📌 Milestone v2.1.0 — Diagnóstico Avançado de Redes e Containers
- [ ] **Métricas de Containers**: Inspeção de containers Docker e Podman (uso de CPU, memória, containers parados e imagens órfãs para limpeza opcional).
- [ ] **Diagnóstico de Rede & Sockets**: Verificação de latência para gateways/DNS configurados, portas abertas em escuta local e saturação de conexões.
- [ ] **Auditoria de Segurança Avançada**: Verificação básica de portas expostas e usuários com privilégios sudo.

### 📌 Milestone v2.2.0 — Integração e Observabilidade
- [ ] **Endpoint / Modo Prometheus Exporter**: Flag `--metrics-exporter` ou saída em formato Prometheus OpenMetrics para raspagem por Prometheus/Grafana Agent.
- [ ] **Notificações e Webhooks**: Envio automático de alertas quando o Health Score ficar abaixo do limiar crítico (suporte a Webhook Discord, Telegram e Slack).

### 📌 Milestone v2.3.0 — Interface Web Opcional e Histórico de Métricas
- [ ] **Dashboard Web Leve Opcional**: Interface web minimalist embutida via FastHTML/Bottle para visualização remota via navegador.
- [ ] **Histórico Temporal de Health Score**: Armazenamento local leve em SQLite (`~/.local/share/sysdoctor/history.db`) para geração de gráficos de tendência ao longo do tempo.
