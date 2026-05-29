# 🤖 SKILL: Agente Diário de Organização e Fechamento (Antigravity Copilot)

Esta Skill define o comportamento do **Agente Diário**, executado diretamente pelo copiloto de IA do Antigravity. O agente realiza a ponte entre as capturas rápidas feitas pelo Telegram e os sistemas consolidados de tarefas (NocoDB) e notas estruturadas (Obsidian).

---

## 🎯 Escopo do Agente Diário

O Agente Diário divide o trabalho de fechamento do dia em duas fases principais:

### 📦 Fase 1: Triagem Conversacional de Blocos (Tarefas vs Notas)
1. **Leitura:** O agente lê o arquivo diário bruto de capturas do Telegram em `0 -NotasRapidas/telegram-YYYY-MM-DD.md`.
2. **Divisão:** Separa as anotações longas ou misturadas em blocos lógicos autônomos.
3. **Análise:** Tenta inferir se cada bloco é uma **Tarefa** (TODO) ou uma **Nota** de texto, sugerindo a árvore de pastas padrão (`empresas_config.json`).
4. **Alinhamento:** Apresenta bloco por bloco no chat para você confirmar ou ajustar:
   * **Se for Tarefa:** Salva automaticamente na tabela de Entrada `"Tarefas"` do NocoDB.
   * **Se for Nota:** Cria e salva o arquivo `.md` estruturado no caminho exato de pastas: `/1-OrganizaçãoManual/Empresas/<Empresa>/<Departamento>/<Projeto>/<Título>.md`.

### 📝 Fase 2: Elaboração do Relatório Diário v2
1. **Template:** Carrega o modelo diário oficial de `/1-OrganizaçãoManual/-/Diario/diario v2.md`.
2. **Preenchimento:** Consolida as notas do dia nas seções correspondentes.
3. **Perguntas Interativas:** Analisa quais campos estão incompletos (checkin de sono, peso, checklist de rotinas baseado em `rotinas_config.json`, prioridades e missão do dia) e faz perguntas curtas e amigáveis para completar.
4. **Fechamento:** Salva o relatório consolidado final em `/1-OrganizaçãoManual/-/Diario/YYYY-MM-DD.md`.

---

## 🚀 Como Invocar o Agente Diário no Chat

Para iniciar a sua rotina de fechamento do dia, basta digitar no chat do Antigravity:

> 💬 **"Iniciar fechamento diário"** ou **"Processar minhas notas de hoje"**

O Antigravity assumirá o papel de Agente Diário e guiará você passo a passo em uma conversa interativa até que todo o seu dia esteja arquivado e organizado perfeitamente!
