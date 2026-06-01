# 🚀 Especificação de Melhorias e Novos Agentes — Hórus System (2026-05-29)

Este documento consolida as ideias, diretrizes e especificações de arquitetura para a evolução do **Hórus System**, capturadas a partir das reflexões de Vinícius Barbarulo em 2026-05-29.

---

## 🏛️ 1. Arquitetura de Agentes & Workers

O sistema deve evoluir para um modelo de agentes especializados atuando em segundo plano (Workers em Python) e skills interativas orquestradas pela IA.

### **A. Agente do Telegram (Monitoramento & Captura)**
* **Modo Silencioso:** O bot apenas escuta e salva as anotações. A única resposta permitida no chat é um simples `"OK, salvo."` para evitar distrações.
* **Captura Multimídia:**
  * **Áudio:** Transcrever automaticamente via IA e salvar o texto no banco de dados com data e hora.
  * **Imagem:** Salvar o anexo em uma pasta dedicada e utilizar visão computacional/IA para transcrever do que se trata a imagem (ideia/contexto).
  * **Texto:** Salvar diretamente no banco de dados associado ao dia de hoje (data e hora).
* **Gatilhos Diários (Rotinas):** O bot envia alertas de rotina (ex: `"R1 agora"`) e salva as respostas do usuário no log de ações para acompanhamento.

### **B. Agente de Atas de Reunião (Reunião Worker)**
* **Entrada:** Arquivos de transcrição gerados em tempo real pelo **Tactiq** (baixados manualmente pelo usuário para uma pasta específica).
* **Ação:** O worker em Python abre a transcrição, resume, extrai tarefas, identifica decisões e atualiza o arquivo `.md` do projeto correspondente.
* **Execução:** Pode rodar em segundo plano de tempos em tempos (cron/rotina) ou ser acionado manualmente via comando.

### **C. Ecossistema de Planejamento (Cima para Baixo)**
Para apoiar a produtividade sob a condição de TDAH e inflexibilidade de pensamento, o planejamento será estruturado de forma hierárquica:
1. **Sonhos (`sonhos.md`):** Arquivo livre de prazos, contendo sonhos reais do usuário, acompanhados de uma análise da IA e um *Score de Vontade*.
2. **Planejador Estratégico (10 Anos -> 5 Anos -> 1 Ano -> 3 Meses -> 1 Mês):** Skills interativas acionadas sob demanda para refinar objetivos de longo prazo por meio de perguntas provocativas da IA.
3. **Planejador Semanal (Semanal Worker):** Focado em definir *mini-projetos* ou *mini-missões* semanais. Permite progredir nos OKRs aos poucos (mesmo que ande apenas `0.1` por semana, garantindo consistência).
4. **O Grilo Falante (Agente de Execução Diária):** Monitora as demandas, ajuda a planejar o dia seguinte, levanta riscos de execução e faz cobranças ativas.

### **D. Worker de Notificações & Integração Google**
* **Google Agenda & Google Tasks:** Monitoramento dinâmico da agenda de trabalho.
* **Alertas Ativos:** O worker identifica compromissos e envia avisos imediatos no Telegram.
* **Lembretes Rápidos:** Mapear tarefas de horário programado (ex: rotinas com prefixo `R-`) e enviar alertas na hora exata, com mecanismo de tolerância a falhas (flag de "já lembrado").

### **E. Worker de Reescrita de Projetos**
* **Registro de Alterações:** Sempre que a IA modificar um arquivo de projeto, a modificação é registrada no banco de dados.
* **Rotina Noturna:** Um worker roda à noite em todos os projetos alterados, reescrevendo-os de forma humanamente legível (Obsidian-friendly) e agrupando as edições da IA na seção `# Alterações da IA`.

---

## 🛠️ 2. Diretrizes Técnicas de Desenvolvimento

* **Antigravity CLI:** Instalação do CLI no terminal CMD do Windows para atuar como motor de LLM.
* **Skills Desacopladas:** Manter a lógica das skills em arquivos Markdown externos para facilitar a edição e o refinamento sem precisar alterar o código Python principal.
* **Subprocessos Python:** Configurar a integração Python -> Antigravity via `subprocess` executando comandos no terminal.
* **Commit Automático:** Implementação de um job que realiza `git commit` automático a cada hora para garantir a preservação do histórico do Vault.
* **Painel ADM:** Construção de uma interface administrativa para visualizar dados do banco de dados e integrar com o Obsidian de forma limpa.
