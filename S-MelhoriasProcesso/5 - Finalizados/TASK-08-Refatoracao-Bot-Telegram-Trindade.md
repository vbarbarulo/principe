# 🤖 TASK-08: Refatoração do Bot do Telegram - Trindade Hórus

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Refatorar o arquivo `bot.py` existente para suportar a orquestração de múltiplos agentes utilizando o framework **Agno (ex-Phidata)**, dividindo as interações nos comportamentos das três personas principais (Amigo/Copiloto, Sargento/Chefe e Estrategista).

---

## 📂 Arquivos Envolvidos
- [MODIFY] [bot.py](file:///c:/Users/vinic/OneDrive/Área de Trabalho/meu agente de IA/bot.py)
- [NEW] `src/agents/agent_orchestrator.py`

---

## 📝 Passo a Passo de Execução

### 1. Criar o Orquestrador de Agentes (`agent_orchestrator.py`)
- Definir e instanciar os 3 agentes do Agno com suas respectivas personas e diretrizes no System Prompt:
  - **O Amigo / Copiloto:** Tom calmo, acolhedor, analítico de sentimentos, focado em suporte empático.
  - **O Sargento / Chefe (Militar Realista):** Tom enérgico, focado em disciplina, direto ao ponto e combativo contra a procrastinação ("sem desculpas!").
  - **O Estrategista:** Focado em planos semanais, planejamento OKR a longo prazo e decomposição de metas complexas.

### 2. Implementar a Alternância Dinâmica de Personas
- Desenvolver um roteador em Python (`Router`) que lê a intenção da mensagem ou comandos do Telegram (ex: `/sargento`, `/amigo`, `/estrategista`) para trocar instantaneamente o agente ativo que processará a resposta.
- Exemplo: Ao reclamar de cansaço ou preguiça com o Sargento ativo, o bot responderá com o estilo firme de cobrança.

### 3. Integrar com a API do Telegram Bot
- Atualizar a escuta de mensagens em `bot.py` para passar o input do usuário pelo orquestrador do Agno.
- Utilizar o `SqlAgentStorage` configurado em `agent.db` para que os agentes retenham o histórico de mensagens recente de forma persistente.

---

## 🧪 Critérios de Aceitação / Validação
- O bot deve responder aos comandos `/sargento`, `/amigo` e `/estrategista` mudando claramente a personalidade, vocabulário e estilo da resposta.
- O histórico de conversas deve persistir no SQLite e as respostas devem levar em consideração o contexto de mensagens anteriores.
- Não deve haver travamentos ou vazamentos de contexto entre as personas.
