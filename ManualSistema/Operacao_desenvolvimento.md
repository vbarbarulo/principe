# 🔄 6. Guias Técnicos de Operação & Desenvolvimento

Esta seção agrupa as diretrizes de execução manuais, comandos de inicialização em segundo plano dos agentes locais e padrões de desenvolvimento de software de alta performance adotados no Príncipe System (Hórus).

---

## 🏛️ 1. Como Operar o Agente Asana (`asana_agent.py`)

O Agente Asana sincroniza tarefas, prioridades e OKRs cadastrados no Asana com o banco PostgreSQL (NocoDB).

### 🚀 Formas de Execução Manual

Você pode executar o agente utilizando as **flags simplificadas (atalhos)** ou o parâmetro `--action`:

* **Executar o Fluxo Completo (Recomendado)**:
  ```bash
  python3 .system/Automações/asana_okr_agent.py --completo
  ```
* **Apenas Baixar Dados Locais (Gera arquivos JSON temporários em `/TempAssana`)**:
  ```bash
  python3 .system/Automações/asana_okr_agent.py --baixar
  ```
* **Apenas Sincronizar com o Banco de Dados (Grava os JSONs no Postgres)**:
  ```bash
  python3 .system/Automações/asana_okr_agent.py --sincronizar
  ```

### ⚙️ Agendamento Automático (Cron)

Para rodar de forma automática em segundo plano no WSL Linux:
1. Abra as tarefas cron: `crontab -e`
2. Adicione a linha de agendamento (Exemplo: todos os dias às 03:00 da manhã):
   ```bash
   0 3 * * * /usr/bin/python3 /mnt/c/principe/.system/Automações/asana_okr_agent.py --completo >> /mnt/c/principe/ArquivoProcessados/TempAssana/sync.log 2>&1
   ```

---

## 🤖 2. Como Operar o Agente do Telegram (`telegram_agent.py`)

O Agente do Telegram gerencia a captura de notas e o envio ativo dos lembretes configurados.

### 🚀 Comandos de Inicialização e Background (WSL Linux)

Para garantir que o robô rode continuamente sem a necessidade de manter o terminal aberto:

* **Iniciar o Agente em Segundo Plano**:
  ```bash
  ./.system/Automações/linux/telegram_agent_bg.sh start
  ```
* **Verificar Status de Execução e Logs**:
  ```bash
  ./.system/Automações/linux/telegram_agent_bg.sh status
  ```
* **Parar o Agente**:
  ```bash
  ./.system/Automações/linux/telegram_agent_bg.sh stop
  ```
* **Reiniciar o Agente**:
  ```bash
  ./.system/Automações/linux/telegram_agent_bg.sh restart
  ```

### 💻 Modo Interativo (Primeiro Plano para Testes)

Se precisar depurar logs ou enviar testes rápidos:
```bash
./.system/Automações/linux/telegram_agent_start.sh
```
*(Use `Ctrl + C` para fechar)*

---

## 🧠 3. Como Operar o Agente de Organização de Pensamentos (`agente_organizar_pensamentos.py`)

Este agente limpa o excesso de informações brutas coletadas ao longo do dia no log do Telegram e as estrutura de forma inteligente por temas no painel ativo do Obsidian.

### 🚀 Formas de Execução Manual (Windows Nativo)

Abra o PowerShell na pasta raiz `c:\principe` e execute:
```powershell
python .system/Automações/agente_organizar_pensamentos.py
```

### ⚙️ Como funciona a limpeza e consolidação:
1. Ele lê o log do dia (`hoje/telegram-YYYY-MM-DD.md`).
2. Agrupa tarefas e insights nos tópicos corretos (Trabalho, Pessoal, Financeiro, Comportamento, etc.).
3. Grava e atualiza o painel unificado em `hoje/pensamentos_organizados.md`.
4. Salva um backup das notas brutas (`telegram-YYYY-MM-DD.md.bak`) e **zera** o arquivo original para novos recebimentos.

---

## 💻 4. Padrões de Desenvolvimento & Gestão de Backlog

O ciclo de desenvolvimento técnico do Príncipe System é centralizado na **Fábrica de Software Unificada** (`AGENTE_DESENVOLVIMENTO.md`).

### 🗣️ Como Solicitar Evoluções no Antigravity:
Sempre que desejar criar um script, consertar um bug ou adicionar funcionalidade, envie no chat do Antigravity:
> *"Antigravity, ative a Skill da **Fábrica de Software Unificada** em `AGENTE_DESENVOLVIMENTO.md` para planejar, arquitetar, codificar e testar a seguinte ideia: [descreva a funcionalidade ou bug]"*

A esteira executará de ponta a ponta as seguintes fases em bloco contínuo:
1. **PO (Refinamento)**: Critérios de aceitação e regras de negócio.
2. **Tech Lead (Engenharia)**: Estruturação de arquivos e arquitetura lógica.
3. **Dev (Código)**: Escrita de códigos robustos, limpos e autocontidos.
4. **QA (Testes)**: Validação unitária e comandos de teste prático.

### 📋 Consulta e Atualização do Kanban Técnico
* **Via Telegram**: Digite o comando `/kanban` no chat com o robô para listar as 10 últimas tarefas do backlog com o respectivo status e branch ativa.
* **Via Terminal**: Execute a query local para visualizar todo o status:
  ```bash
  sqlite3 agent.db "SELECT id, status, titulo FROM kanban_tasks ORDER BY id DESC;"
  ```
* **Conclusão de Tarefas**:
  1. Atualize o status no banco local:
     ```sql
     sqlite3 agent.db "UPDATE kanban_tasks SET status = 'done' WHERE id = 'ID_TAREFA';"
     ```
  2. Mescle a branch correspondente no repositório Git.
