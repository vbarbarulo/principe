# 🤖 Como Rodar o Agente do Telegram — Guia de Comandos

Este guia descreve os comandos disponíveis e como operar o **Agente do Telegram** em segundo plano (*background*) ou de forma interativa.

---

## 🚀 1. Executando o Agente em Segundo Plano (*Background*)

Para rodar o agente sem a necessidade de manter o terminal aberto, utilize o gerenciador automatizado:

*   **Iniciar o Agente:**
    ```bash
    ./Z-exe/telegram_agent_bg.sh start
    ```
    *(Inicia o processo oculto, salvando logs em `S-Agentes/Agentes/telegram_agent.log`)*

*   **Verificar se está rodando (Status):**
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

## 💻 2. Executando em Primeiro Plano (Modo Interativo)

Caso queira ver as mensagens chegando no terminal em tempo real (útil para testes rápidos):

```bash
./Z-exe/telegram_agent_start.sh
```
*(Use `Ctrl + C` para encerrar)*

---

## 📂 3. Salvamento de Notas e Lembretes

*   **Notas Diárias:** Toda mensagem enviada para o bot é gravada em um arquivo diário dentro da pasta `0 -NotasRapidas/Diario/YYYY-MM-DD.md`.
*   **Lembretes Automáticos:** O bot envia lembretes programados ao longo do dia nos seguintes horários padrão:
    *   **09:00** — Planejamento matinal e metas 🚀
    *   **13:30** — Lembrete de hidratação e progresso 💧
    *   **18:00** — Encerramento de expediente e revisão diária 📝
    *   **21:30** — Desacelerar e descansar 💤
