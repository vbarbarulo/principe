# 🛠️ Skill Specification: Daily Note Processor & Orchestrator (v2)

### **Descrição Geral**
Esta skill processa o arquivo de nota diária (`Daily Note` ou capturas brutas do Telegram) do Obsidian, consolidando o histórico do dia em um relatório executivo de suporte ao TDAH e distribuindo as informações categorizadas para seus respectivos destinos (NocoDB, Pastas de Projetos ou Diário Pessoal), otimizando o uso de LLM (Single-pass Extraction) para reduzir custos e latência.

---

### **1. Inputs (Entradas)**
* **`daily_note_text`**: O conteúdo textual bruto coletado do dia (ex: `0 -NotasRapidas/telegram-YYYY-MM-DD.md` ou nota diária ativa).
* **`mapping_matrix_json`**: O mapa em JSON contendo a estrutura de `Empresa -> Departamento -> Projeto` (`empresas_config.json`).
* **`rotinas_config.json`**: Metas e checklists de hábitos diários (sono, peso, exercícios).

---

### **2. Pipeline de Processamento (Passo a Passo)**

#### **Fase 1: Orquestração e Roteamento Inteligente (Single-pass JSON)**
O agente executa uma única chamada estruturada para separar os blocos de informação em três grandes categorias:
* **Tarefas (Microgerenciamento):** Ações pendentes, cobranças pendentes e status de tarefas.
  * *Inteligência:* Extrai e calcula datas relativas (ex: "até amanhã" -> calcula `YYYY-MM-DD`).
  * *Ação:* Prepara a chamada para a API do **NocoDB** (com fallback de fila local `.offline_tasks_queue.json` se a API estiver fora do ar).
* **Projetos / Negócios:** Atas de reuniões, análises técnicas ou documentos de projetos.
  * *Ação:* Localiza a pasta correta com base na matriz de mapeamento e atualiza (ou apensa no final de) arquivos `.md` correspondentes em `/1-OrganizaçãoManual/Empresas/`.
* **Vida Pessoal (Dump & Tag Later):** Reflexões, memórias, insights e momentos familiares.
  * *Ação:* Isola este bloco, consolida com o Relatório Executivo e salva a Nota Diária final em `/Z-ArquivosProcessados/Diario/YYYY-MM-DD.md`.

> ⚠️ **Regra de Ouro (Human-in-the-Loop):** O agente apresenta um resumo rápido das ações propostas no chat antes de persistir os dados no NocoDB e Obsidian, permitindo ajustes de última hora.

#### **Fase 2: Consolidação (Relatório Executivo TDAH-Friendly)**
Gerar um resumo de no máximo duas linhas por grande acontecimento do dia, garantindo foco e rapidez na leitura.
* *Destaque de Bloqueios:* Itens marcados como impedidos ou urgentes recebem destaque imediato `⚠️`.

#### **Fase 3: Extração de Metadados (Nuvem de Contexto)**
Extração de palavras-chave estruturadas para alimentar buscas futuras:
* **Profissional:** Termos técnicos e projetos de maior foco no dia.
* **Pessoal:** Sentimentos predominantes e tópicos de reflexão.

---

### **3. Estratégia de Arquivamento e Lote Retroativo**
* **Projetos e Tarefas:** Mantidos rigorosamente na hierarquia de pastas padrão.
* **Diário Pessoal:** Consolidação diária na pasta central de arquivamento. A cada final de semana, a IA executa uma rotina em lote para analisar os textos acumulados e sugerir tags retroativas inteligentes (`#memórias`, `#insights`, `#crescimento-pessoal`).

---

### **4. Outputs (Saídas da Skill)**
* Tabelas atualizadas no **NocoDB**.
* Arquivos `.md` de projetos atualizados de forma incremental no **Obsidian**.
* **Nota Diária Final (Relatório Executivo + Diário Pessoal + Tracker)** salva em `/Z-ArquivosProcessados/Diario/YYYY-MM-DD.md`.
* **Notificação Executiva** despachada para o Telegram.

---

### **5. Como Invocar o Agente Diário**
Para iniciar a sua rotina de fechamento do dia, basta digitar no chat do Antigravity:
> 💬 **"Iniciar fechamento diário"** ou **"Processar minhas notas de hoje"**
