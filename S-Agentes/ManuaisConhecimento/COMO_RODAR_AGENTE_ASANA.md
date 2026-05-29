# 🔄 Como Rodar o Agente Asana — Manual de Operação

Este manual descreve detalhadamente como executar o **Agente Asana** do Hórus System, seja manualmente via linha de comando ou definindo rotinas de agendamento automático.

---

## 🚀 1. Formas de Execução Manual

Você pode executar o agente de duas maneiras equivalentes: usando as **flags simplificadas** (atalhos) ou o parâmetro `--action`.

### Método A: Utilizando Atalhos Rápidos (Recomendado)

*   **Apenas Baixar os Dados Locais:**
    ```bash
    python3 S-Agentes/Agentes/asana_agent.py --baixar
    ```
    *(Gera e atualiza os arquivos em `Z-ArquivosProcessados/TempAssana`)*

*   **Apenas Sincronizar com o Banco (PostgreSQL):**
    ```bash
    python3 S-Agentes/Agentes/asana_agent.py --sincronizar
    ```
    *(Lê os arquivos baixados localmente, remove duplicadas e grava no Postgres)*

*   **Executar o Fluxo Completo (Baixar + Sincronizar):**
    ```bash
    python3 S-Agentes/Agentes/asana_agent.py --completo
    ```

---

### Método B: Utilizando a flag `--action`

Se preferir o formato de parâmetro tradicional:

*   **Baixar os dados:**
    ```bash
    python3 S-Agentes/Agentes/asana_agent.py --action baixar
    ```
*   **Sincronizar:**
    ```bash
    python3 S-Agentes/Agentes/asana_agent.py --action sincronizar
    ```
*   **Fluxo Completo:**
    ```bash
    python3 S-Agentes/Agentes/asana_agent.py --action completo
    ```

---

## ⚙️ 2. Como Configurar na Rotina do Sistema (Cron)

Para automatizar a execução diária ou de hora em hora:

1.  Abra o editor de tarefas do Linux:
    ```bash
    crontab -e
    ```
2.  Adicione a linha desejada na parte inferior do arquivo:

    *   **Todos os dias às 03:00 da manhã (Recomendado):**
        ```bash
        0 3 * * * /usr/bin/python3 /mnt/c/principe/S-Agentes/Agentes/asana_agent.py --completo >> /mnt/c/principe/Z-ArquivosProcessados/TempAssana/sync.log 2>&1
        ```
    *   **A cada 1 hora:**
        ```bash
        0 * * * * /usr/bin/python3 /mnt/c/principe/S-Agentes/Agentes/asana_agent.py --completo >> /mnt/c/principe/Z-ArquivosProcessados/TempAssana/sync.log 2>&1
        ```

3.  Salve e feche o editor. Os logs de execução serão salvos em `/mnt/c/principe/Z-ArquivosProcessados/TempAssana/sync.log`.

---

## 📂 3. Diretórios Utilizados pelo Agente
*   **Script do Agente:** `S-Agentes/Agentes/asana_agent.py`
*   **Dados Temporários:** `Z-ArquivosProcessados/TempAssana/okr_tasks.json` e `prioridades_tasks.json`
*   **Configurações e Chaves:** `.env` (na raiz do projeto)
