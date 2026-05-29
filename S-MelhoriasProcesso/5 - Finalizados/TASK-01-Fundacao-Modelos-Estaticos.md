# 🗂️ TASK-01: Fundação & Modelos Estáticos

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Estruturar o ambiente de configuração inicial do Projeto Hórus, fornecendo suporte a configurações de estrutura organizacional, metas temporais (`config.json`) e rotinas em formato de marcação Markdown simplificado (`rotinas.md`), além de criar um parser robusto em Python capaz de ler estas rotinas.

---

## 📂 Arquivos Envolvidos
- [NEW] `config/config.json`
- [NEW] `config/rotinas.md`
- [NEW] `src/utils/rotinas_parser.py`

---

## 📝 Passo a Passo de Execução

### 1. Criar pasta de configurações
- Criar a pasta `config/` na raiz do projeto.

### 2. Criar `config/config.json`
- Definir empresas, departamentos, projetos e o sistema de tags padrão conforme as orientações:
  - Tags de Emoções (`culpa`, `orgulho`, `ansiedade`, `foco`, `energia`, `tedio`).
  - Tags de Tipos (`tarefa`, `projeto`, `nota`, `meta`).
  - Tags de Tempo (`hoje`, `semana`, `mes`, `ano`, `vida`).
  - Tags de Curva de Prioridade (`A`, `B`, `C`).

### 3. Criar `config/rotinas.md`
- Escrever o arquivo de rotinas detalhado com os blocos de horários em Markdown (ex: `## 🌅 Rotina Acordar [06:00]`), listando tarefas e sub-tarefas com checkboxes `- [ ]`.

### 4. Desenvolver o Parser `rotinas_parser.py`
- Criar um script Python com expressões regulares para ler e analisar `rotinas.md`.
- Extrair:
  - Nome do bloco e horário associado.
  - Hierarquia de tarefas (itens e sub-itens indentados).
  - Gerar um ID técnico hash ou sequencial único para cada sub-ação (ex: `RM1_01`, `RM1_02`).

---

## 🧪 Critérios de Aceitação / Validação
- O arquivo `config.json` deve ser um JSON válido.
- O script `rotinas_parser.py` deve ler `rotinas.md` sem gerar erros de formatação.
- A saída do parser deve retornar uma lista estruturada de dicionários/objetos contendo o bloco, horário, tarefa e IDs exclusivos gerados para cada tarefa e sub-tarefa.
