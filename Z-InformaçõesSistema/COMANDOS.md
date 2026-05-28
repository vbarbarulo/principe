# 📜 Guia Rápido de Comandos — Hórus System

Este é o seu guia rápido de consulta de comandos do **Hórus System**. Guarde este arquivo na raiz do seu projeto para consulta rápida no Obsidian ou qualquer outro editor de texto.

---

## 🎖️ A Trindade de Personas
Comandos para alternar o tom e a personalidade das respostas da Inteligência Artificial:

| Comando | Persona | Foco principal | Tom da Conversa |
| :--- | :--- | :--- | :--- |
| **`/sargento`** | 🎖️ O Sargento | Combate implacável à paralisia do TDAH e à procrastinação. | Duro, militar, direto e realista. |
| **`/amigo`** | 🧠 O Amigo/Copiloto | Suporte emocional, escuta ativa e acolhimento. | Empático, carinhoso e focado em sentimentos. |
| **`/estrategista`** | 📈 O Estrategista | Planejamento tático de médio/longo prazo (OKRs). | Analítico, pragmático e focado em sprints semanais. |

---

## 🔹 Operações Diárias
Comandos para registrar seus hábitos, saúde e reflexões ao longo do dia:

*   **`/start`**
    *   *O que faz*: Inicializa a sessão com o bot, ativa a persona padrão (Sargento) e mostra o menu principal.
*   **`/checkin`**
    *   *O que faz*: Inicia o fluxo interativo de saúde matinal.
    *   *Perguntas realizadas*:
        1. 💤 Horário que foi dormir ontem
        2. ⏰ Horário que acordou hoje
        3. ⭐ Avaliação subjetiva do sono (1 a 5)
        4. ⚖️ Peso diário em kg (Integra com o *Upsert Engine*)
        5. 📝 Breve relato emocional ao acordar
*   **`/descomprimir`**
    *   *O que faz*: Inicia o encerramento do dia. Cole um texto longo ou grave um desabafo sobre o seu dia. A IA extrairá automaticamente:
        *   Pontos excelentes e lições aprendidas
        *   Dificuldades e sentimentos identificados
        *   **Tarefas automáticas para o Segundo Cérebro** (Classificando-as na Curva ABC: `A`, `B` ou `C`)
*   **`/relatorio`**
    *   *O que faz*: Sincroniza e consolida todas as informações no seu **Obsidian Vault** local.
    *   *Resultado*: Salva uma nota formatada em Markdown no diretório `diarios/`.
*   **`/memoria`**
    *   *O que faz*: Ativa o modo de busca semântica (**RAG local**).
    *   *Exemplo*: Você pode perguntar coisas como *"Quando foi a última vez que me senti cansado?"* ou *"O que eu decidi na descompressão de terça-feira?"* e o Hórus buscará em seus relatórios passados.

---

## 🛠️ Esteira de Desenvolvimento (Kanban)
Seu sistema é capaz de codificar e evoluir de forma autônoma por meio de um pipeline de agentes especializados:

*   **`/nova_task [ideia]`**
    *   *O que faz*: Informa que a gestão e o refinamento do backlog foram migrados para o **Antigravity**. Use os arquivos da pasta `skills/` no seu IDE local para refinar novas ideias com segurança!
*   **`/aprovar_task [ID]`**
    *   *O que faz*: Redireciona você para executar e testar sua tarefa localmente de forma pareada com o **Antigravity**, garantindo controle absoluto de código e evitando quebras no servidor.
*   **`/kanban`**
    *   *O que faz*: Exibe o quadro Kanban atual com as últimas 10 tarefas do banco de dados, seus status (`backlog`, `refining`, `developing`, `testing`, `done`, `blocked`) e a branch ativa.

---

## 📂 Pasta de Skills (Desenvolvimento Local com o Antigravity)
Agora, em vez de agentes autônomos tomarem decisões sozinhos no servidor, nós trabalhamos juntos como um time completo de desenvolvimento de elite diretamente no **Antigravity**:

*   🧠 **`skills/1_product_owner.md`**: Focada em refinamento de ideias brutas, priorização e definição de critérios de aceitação.
*   ⚙️ **`skills/2_tech_lead.md`**: Focada em mapeamento de impacto, planejamento de arquitetura e arquivos afetados.
*   💻 **`skills/3_developer.md`**: Focada em codificação limpa, robusta e aderente aos padrões do projeto.
*   🧪 **`skills/4_qa_tester.md`**: Focada em planos de testes unitários e validação no ambiente local.
*   🚀 **`skills/sprint_orchestrator.md`**: O guia definitivo explicando como nós dois coordenamos as sprints e rodamos cada persona.

---

## 📚 Manuais e Ajuda
*   **`/help`**
    *   *O que faz*: Exibe um guia rápido com todos os comandos resumidos diretamente no chat.
*   **`/help_d`**
    *   *O que faz*: Exibe um manual operacional e técnico detalhado contendo a explicação aprofundada dos fluxos.

---

> [!TIP]
> **Você sabia?** As personas conversacionais do Hórus têm autoconsciência de sua estrutura local. Você pode perguntar a elas no chat normal coisas como: *"Quais tabelas existem no meu banco de dados?"* ou *"Como está estruturado meu projeto?"* e elas responderão com precisão!
