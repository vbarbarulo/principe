# ⏰ TASK-09: Agendador de Lembretes Proativos

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Implementar um sistema de agendamento de tarefas em segundo plano (background tasks) no Python para que o bot do Telegram atue ativamente nos "horários-gatilho" das rotinas definidas em `rotinas.md`, cobrando o usuário e fornecendo lembretes essenciais para evitar a procrastinação.

---

## 📂 Arquivos Envolvidos
- [MODIFY] [bot.py](file:///c:/Users/vinic/OneDrive/Área de Trabalho/meu agente de IA/bot.py)
- [NEW] `src/scheduler/routine_scheduler.py`

---

## 📝 Passo a Passo de Execução

### 1. Criar o Agendador Base (`routine_scheduler.py`)
- Utilizar uma biblioteca robusta de agendamento em Python (ex: `APScheduler` ou o loop de eventos nativo do Python/FastAPI).
- O script deve inicializar lendo os horários das rotinas ativas em `rotinas.md` (por meio do parser criado na `TASK-01`).

### 2. Configurar os Gatilhos Ativos
- Para cada rotina encontrada (ex: `Rotina Acordar [06:00]`), registrar um agendamento diário para aquele horário.
- Quando o gatilho disparar, o bot deve enviar uma mensagem ativa pelo Telegram iniciada pela persona do **Sargento** cobrando a execução daquela rotina e listando seus micro-passos.

### 3. Mecanismo de Confirmação Ativa
- Se o usuário não responder confirmando a execução da rotina ou reportando o que cumpriu/pulou em até 30 minutos, enviar uma cobrança secundária mais incisiva.

---

## 🧪 Critérios de Aceitação / Validação
- O sistema de agendamento deve rodar em segundo plano acoplado à execução do `bot.py`.
- No horário programado, a mensagem contendo o lembrete ativo da rotina correspondente deve ser disparada com sucesso no chat do Telegram configurado.
- Os lembretes secundários devem parar imediatamente após o usuário responder.
