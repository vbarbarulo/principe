# 👑 HÓRUS SYSTEM — MANUAL TÉCNICO & GUIA OPERACIONAL DO USUÁRIO

Bem-vindo ao **QG Hórus**, o seu ecossistema pessoal de produtividade e desenvolvimento assistido por inteligência artificial. Este manual documenta de forma minuciosa tanto o **funcionamento operacional** (comandos do Telegram, rotinas diárias e integração com o Obsidian) quanto a **arquitetura técnica** interna (banco de dados SQLite, orquestrador de personas e pipeline de desenvolvimento Kanban).

---

## 📂 1. Estrutura Física do Projeto (Arquivos e Diretórios)

O ecossistema local do Hórus System está organizado da seguinte forma no seu repositório:

```text
meu agente de IA/
├── agent.db                  # Banco de dados central SQLite
├── bot.py                    # Script principal do Bot do Telegram
├── database.py               # Script de inicialização e definição do Schema do banco
├── start_sargento.bat        # Arquivo em lote para inicialização rápida no Windows via WSL
├── config/
│   ├── config.json           # Configurações de empresas, departamentos e tags padrão
│   └── obsidian_templates/   # Modelos Markdown de Dashboards do Obsidian
├── diarios/                  # Diretorio de notas diárias e relatórios de progresso (Sincronizado com o Vault)
├── scripts/
│   ├── backup.py             # Script automatizado para backup de segurança do agent.db
│   ├── import_backlog.py     # Script útil para parser e inserção de tarefas do backlog
│   ├── reboot.sh             # Script Unix de reinicialização rápida
│   └── reboot_windows.bat    # Script Windows de reinicialização rápida
├── src/
│   ├── agents/
│   │   ├── agent_orchestrator.py   # Orquestrador das Personas (Sargento, Amigo, Estrategista)
│   │   ├── decompression_agent.py  # Processador da Descompressão ativa de final de dia
│   │   ├── dev_team.py             # Agentes da Equipe de Dev (PO, Tech Lead, Dev, QA)
│   │   ├── kanban_pipeline.py      # Automação do pipeline Kanban (Git + Testes + Auto-Correção)
│   │   └── memory_rag.py           # Mecanismo de busca semântica em memórias passadas
│   ├── database/
│   │   └── upsert_engine.py        # Motor de inteligência para Upserts de hábitos e rotinas
│   ├── obsidian/
│   │   └── vault_sync.py           # Sincronização bidirecional de notas físicas com o banco de dados
│   ├── scheduler/
│   │   └── routine_scheduler.py    # Agendador ativo de lembretes e alarmes de rotina
│   └── utils/
│       ├── git_utils.py            # Wrappers para comandos de Versionamento Git
│       └── rotinas_parser.py       # Parser de rotinas do Obsidian para o banco de dados
└── tests/                    # Diretório onde são gravados e rodados os testes automáticos de QA
```

---

## 🗃️ 2. Arquitetura de Dados (Banco Híbrido SQLite)

O banco relacional `agent.db` possui **8 tabelas principais** para orquestrar dados, hábitos, telemetria e o fluxo do Kanban técnico:

1. **`rotinas_log`**: Logs de conclusão de rotinas diárias com percentual de KPIs.
2. **`checkin_saude`**: Histórico diário de sono (hora de dormir, acordar, qualidade), peso e relatórios de bem-estar.
3. **`logs_descompressao`**: Registros brutos do encerramento do dia, com a respectiva análise da IA e as decisões tomadas.
4. **`conversas_insights`**: Notas, insights e diálogos relevantes gerados na interação.
5. **`registros_rotina`**: Estado consolidado das ações concluídas/puladas do dia organizadas por blocos de rotina (ex: "acordar", "dormir").
6. **`itens_segundo_cerebro`**: Backlog geral de ideias, tarefas e notas classificadas na Curva ABC (`A`, `B` ou `C`) e prontas para sincronia com o Obsidian.
7. **`memorias_usuario`**: Memórias semânticas persistidas (grau de preferência, emoções, sentimentos e fatos marcantes).
8. **`kanban_tasks`**: Quadro do ciclo de desenvolvimento de software onde são geridos os cards da esteira de automação (`status`: `backlog`, `refining`, `developing`, `testing`, `done`, `blocked`).

---

## 🧠 3. A Trindade de Personas (Orquestrador de IA)

O Hórus System conta com 3 personas especializadas para interagir via Telegram, alternando o tom conforme sua necessidade atual:

*   **🎖️ O Sargento (`/sargento`)**:
    *   *Foco*: Combate implacável à paralisia do TDAH e à procrastinação.
    *   *Tom*: Duro, realista, direto e militar. Ele não aceita desculpas e exige ação.
*   **🧠 O Amigo/Copiloto (`/amigo`)**:
    *   *Foco*: Suporte emocional, escuta ativa e validação psicológica.
    *   *Tom*: Empático, carinhoso, analítico de sentimentos. Excelente para desabafos e reflexões.
*   **📈 O Estrategista (`/estrategista`)**:
    *   *Foco*: Planejamento tático de médio e longo prazo (OKRs).
    *   *Tom*: Analítico, pragmático. Especialista em quebrar grandes ideias em sprints semanais simples.

---

## 🤖 4. Guia de Comandos do Bot do Telegram

### 📡 Comandos Operacionais

*   **`/start`**: Inicializa a sessão, ativa a persona padrão (Sargento) e exibe o menu principal.
*   **`/checkin`**: Fluxo interativo e guiado de saúde matinal:
    1. Pergunta horário de dormir.
    2. Horário de acordar.
    3. Avaliação subjetiva do sono (1 a 5).
    4. Peso diário (kg) - *Integra-se automaticamente com o Upsert Engine para a rotina diária*.
    5. Breve relato emocional ao acordar.
*   **`/descomprimir`**: Inicia o modo de descompressão ativa de fim de dia. O usuário pode colar uma nota bruta, desabafo ou transcrição de áudio e a IA extrai automaticamente:
    *   Pontos excelentes e lições aprendidas.
    *   Dificultadores e sentimentos identificados.
    *   **Novas tarefas do segundo cérebro**, classificando-as na curva ABC e sincronizando-as com o Obsidian.
*   **`/relatorio`**: Consolida os hábitos, peso, check-in e tarefas do dia em uma nota física formatada em Markdown no diretório `diarios/` e realiza o sincronismo.
*   **`/memoria`**: Realiza buscas semânticas (RAG) em relatórios anteriores, permitindo responder perguntas contextuais sobre o histórico pessoal.

### 🛠️ Comandos do Kanban de Desenvolvimento

O sistema é autossuficiente em termos de desenvolvimento de novos recursos de código através de agentes especializados:

*   **`/nova_task [ideia]`**: Envia uma ideia bruta de melhoria de software. O agente **Product Owner (PO)** analisa a ideia, refina os requisitos técnicos funcionais, classifica a prioridade na Curva ABC, cria um registro em `kanban_tasks` (status `refining`) e atribui um ID único.
*   **`/aprovar_task [ID]`**: Dispara o pipeline de desenvolvimento automatizado:
    1. **Tech Lead** avalia a viabilidade arquitetural, mapeia os arquivos afetados e descreve as subtarefas do backend/frontend/prompt (status muda para `developing`).
    2. **Dev Senior** codifica todas as mudanças necessárias.
    3. **QA Planner** cria testes unitários em python integrados na pasta `tests/` (status muda para `testing`).
    4. **QA Executável** executa os testes no WSL. Se falharem, aciona a **auto-correção** por até 3 rodadas.
    5. **Finalização**: Se os testes passarem, o código é commitado em Git na branch dedicada `task-[id]`, mesclado à `master`, e o card muda para `done`. Um relatório detalhado é gerado em `diarios/relatorio_[id].md`.
*   **`/kanban`**: Exibe o quadro Kanban completo com o status e a branch de cada tarefa de desenvolvimento de software ativa.

---

## 🛠️ 5. Como Operar o Sistema Localmente

1. **Inicialização rápida**:
   * Dê duplo clique em `start_sargento.bat` no seu Windows.
   * O script iniciará o WSL Ubuntu e subirá o bot de forma persistente através do comando `wsl python3 bot.py`.
2. **Consultar logs**:
   * Os relatórios de progresso do dia e as entregas do Kanban de desenvolvimento são gravados localmente em Markdown no diretório `diarios/` para serem facilmente visualizados e anexados no Obsidian.
