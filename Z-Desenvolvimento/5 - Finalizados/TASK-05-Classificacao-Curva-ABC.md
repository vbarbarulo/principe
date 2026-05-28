# 📊 TASK-05: Lógica de Classificação da Curva ABC

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Desenvolver o módulo cognitivo que categoriza automaticamente as tarefas capturadas durante a conversa ou descompressão diária seguindo as diretrizes metodológicas da Curva ABC (Priorização Baseada em Consequências).

---

## 📂 Arquivos Envolvidos
- [NEW] `src/agents/abc_classifier.py`
- [MODIFY] `src/agents/decompression_agent.py`

---

## 📝 Passo a Passo de Execução

### 1. Definir o Prompt do Classificador ABC
- Configurar o LLM com regras claras de classificação:
  - **Curva A:** Alta consequência se não for feita no dia (prazos rígidos de trabalho, saúde essencial).
  - **Curva B:** Média consequência / Importante para médio e longo prazo (estudos, projetos em andamento, manutenção preventiva).
  - **Curva C:** Baixa consequência / Seria bom fazer, mas sem impacto crítico se adiado (atividades recreativas soltas, ideias sem prazo).

### 2. Implementar a Regra de Não-Acúmulo no Inbox
- Codificar a lógica no Python:
  - Se uma tarefa Curva A ou B planejada para "hoje" não for concluída, o sistema **não** a devolve para a caixa de entrada (inbox).
  - O robô simplesmente altera o metadado `data_registro` ou `data_planejada` para o dia seguinte de forma automática, mantendo sua classificação de prioridade intacta.

### 3. Persistência na Tabela `itens_segundo_cerebro`
- Gravar o item no banco SQLite preenchendo o campo `curva` (`A`, `B` ou `C`), `tempo` (`hoje`, `semana`, `mes`) e as tags contextuais detectadas pela IA.

---

## 🧪 Critérios de Aceitação / Validação
- Ao enviar o texto *"Tenho que pagar o boleto da internet hoje senão vão cortar"* para o classificador, a tarefa correspondente deve ser classificada automaticamente como **Curva A** e planejada para **hoje**.
- Ao enviar *"Queria pesquisar mais sobre novas técnicas de jardinagem um dia desses"*, a tarefa correspondente deve ser classificada como **Curva C** ou **Nota**.
- Testar e validar que tarefas pendentes mudam de data sem voltar para o inbox.
