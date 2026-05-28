# 📊 TASK-07: Painéis e Consultas Dataview no Obsidian

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Estruturar os templates de visualização dentro do Obsidian Vault, utilizando consultas nativas dos plugins **Dataview** e **Tracker** para gerar dashboards visuais automáticos de hábitos, progresso de projetos e controle comportamental.

---

## 📂 Arquivos Envolvidos
- [NEW] `config/obsidian_templates/Template-Nota-Diaria.md`
- [NEW] `config/obsidian_templates/Dashboard-Horus.md`

---

## 📝 Passo a Passo de Execução

### 1. Criar Template de Nota Diária
- Criar a estrutura Markdown padrão que será clonada pela IA ou pelo Obsidian.
- Incluir tags do sistema Dataview para rastrear sono, humor e consistência de hábitos diários.

### 2. Desenvolver as Consultas DataviewJS / Dataview
- No arquivo `Dashboard-Horus.md`, inserir blocos de código Dataview para listar:
  - Todas as tarefas pendentes classificadas como **Curva A** (`#tarefa` e `curva: A`).
  - Tarefas secundárias do dia (`Curva B`).
  - O histórico recente dos logs de descompressão.

### 3. Integrar Consultas do Obsidian Tracker (Hábitos)
- Criar blocos de configuração do plugin **Obsidian Tracker** para buscar os valores numéricos de `peso_kg` ou `nota_sono` do frontmatter YAML das notas diárias e renderizar gráficos de linha e calendários de consistência diretamente no Obsidian.

---

## 🧪 Critérios de Aceitação / Validação
- O arquivo `Dashboard-Horus.md` deve listar com precisão as notas que contêm as chaves YAML desejadas ao ser aberto dentro do Obsidian com o plugin Dataview ativo.
- Os templates de gráfico do Tracker não devem conter erros de sintaxe YAML e devem renderizar as métricas de forma limpa.
