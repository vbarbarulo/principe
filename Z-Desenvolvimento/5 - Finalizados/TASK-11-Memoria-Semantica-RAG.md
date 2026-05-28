# 🧠 TASK-11: RAG de Longo Prazo e Memória Semântica

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Implementar a inteligência de memória de longo prazo e pesquisa semântica do Hórus, utilizando **LlamaIndex** e o modelo local do **Ollama** para permitir que o usuário faça perguntas subjetivas e recupere sentimentos ou memórias antigas.

---

## 📂 Arquivos Envolvidos
- [NEW] `src/agents/memory_rag.py`
- [MODIFY] `src/agents/agent_orchestrator.py`

---

## 📝 Passo a Passo de Execução

### 1. Configurar a Inicialização do LlamaIndex Local
- Configurar o motor do LlamaIndex para apontar para a pasta local de notas diárias do Obsidian (`diarios/` ou a pasta do Obsidian Vault).
- Utilizar os embeddings locais (ex: `nomic-embed-text` ou equivalente leve do Ollama) para indexar os textos Markdown e o histórico de descompressão.

### 2. Implementar a Busca por Similaridade Semântica
- Criar a ferramenta de busca (`QueryEngine`) em Python.
- Exemplo: Quando o usuário pergunta *"quando foi a última vez que me senti muito cansado?"*, o sistema pesquisa no banco vetorial local por similaridade semântica e injeta os trechos relevantes no prompt do agente.

### 3. Gerenciamento e Consolidação Contínua de Memória (Fatos)
- Criar um script de consolidação diária que lê a tabela `memorias_usuario` e as conversas recentes, detectando fatos repetidos ou mudanças de preferência para atualizar a base de conhecimento estática injetada no prompt (Controlando o custo de tokens).

---

## 🧪 Critérios de Aceitação / Validação
- O sistema deve ser capaz de criar e manter atualizado um índice vetorial na pasta do projeto sem gargalos de CPU.
- Ao fazer perguntas ao bot sobre fatos do passado relatados em diários antigos, a IA deve citar as datas exatas e o contexto das notas recuperadas.
