# 🤖 Como Rodar o Agente do Telegram — Manual de Operação

Este manual descreve detalhadamente como executar o **Agente do Telegram** do Príncipe System, projetado para capturar notas diárias e enviar lembretes úteis ao longo do dia de forma 100% autônoma.

---

## 🚀 1. Formas de Execução

Você pode executar o agente de duas maneiras: em primeiro plano (para testes rápidos) ou em segundo plano (*background*).

### Método A: Execução em Segundo Plano (Recomendado)

Foi desenvolvido um gerenciador completo que permite iniciar, parar, reiniciar e ver o status do bot sem manter o terminal aberto.

*   **Iniciar o Agente em Segundo Plano:**
    ```bash
    ./Z-exe/telegram_agent_bg.sh start
    ```
    *(Gera e atualiza os logs em `S-Agentes/Agentes/telegram_agent.log` e cria o arquivo de PID em `S-Agentes/Agentes/telegram_agent.pid`)*

*   **Verificar o Status (Se está ativo e os últimos logs):**
    ```bash
    ./Z-exe/telegram_agent_bg.sh status
    ```

*   **Parar o Agente:**
    ```bash
    ./Z-exe/telegram_agent_bg.sh stop
    ```

*   **Reiniciar o Agente:**
    ```bash
    ./Z-exe/telegram_agent_bg.sh restart
    ```

---

### Método B: Execução Interativa em Primeiro Plano

Ideal para quando você está depurando o código ou quer ver a saída em tempo real no console:

```bash
./Z-exe/telegram_agent_start.sh
```
*(Para parar a execução, basta usar `Ctrl + C` no terminal)*

---

## 📂 2. Como Funciona a Captura de Notas

O agente lê a chave `TELEGRAM_TOKEN` no seu arquivo `.env` principal e inicia a escuta.
*   **Identificação:** Na primeira mensagem que você enviar para o bot, ele registrará o seu `chat_id` localmente no arquivo de estado (`telegram_agent_state.json`).
*   **Anotações Diárias:** Toda mensagem de texto que você enviar para ele a partir de então será acrescentada em um arquivo diário formatado em Markdown dentro de:
    `hoje/Diario/YYYY-MM-DD.md`
*   **Formato de Registro:**
    ```markdown
    - [HH:MM:SS] Sua mensagem enviada aqui
    ```

---

## ⏰ 3. Lembretes Automáticos Programados

O bot possui uma thread dedicada que monitora o relógio e dispara mensagens ativas em horários predefinidos:
*   **09:00** — 🌅 Planejamento e metas do dia.
*   **13:30** — 💧 Lembrete de hidratação e progresso.
*   **18:00** — 📝 Revisão de tarefas e fechamento de expediente.
*   **21:30** — 💤 Lembrete para desacelerar e descansar.

---

## 📂 4. Diretórios e Arquivos Utilizados pelo Agente
*   **Script do Agente:** `S-Agentes/Agentes/telegram_agent.py`
*   **Script de Inicialização:** `Z-exe/telegram_agent_start.sh`
*   **Gerenciador de Background:** `Z-exe/telegram_agent_bg.sh`
*   **Log de Execução:** `S-Agentes/Agentes/telegram_agent.log`
*   **Notas Salvas:** `hoje/Diario/`
