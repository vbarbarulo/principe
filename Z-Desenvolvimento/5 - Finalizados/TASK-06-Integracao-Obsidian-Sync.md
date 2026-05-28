# 🔌 TASK-06: Sincronização Ativa com Obsidian Vault

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Implementar o módulo Python encarregado de ler os dados estruturados no banco SQLite local (`registros_rotina`, `itens_segundo_cerebro`) e exportar Notas Diárias e Notas de Projeto estruturadas em Markdown (.md) diretamente para a pasta do Obsidian Vault do usuário.

---

## 📂 Arquivos Envolvidos
- [NEW] `src/obsidian/vault_sync.py`
- [MODIFY] [database.py](file:///c:/Users/vinic/OneDrive/Área de Trabalho/meu agente de IA/database.py)

---

## 📝 Passo a Passo de Execução

### 1. Mapear o Caminho do Obsidian Vault
- Definir uma variável de ambiente ou configuração no `config.json` com o caminho físico absoluto da pasta do Obsidian Vault do usuário.

### 2. Desenvolver o Gerador de Frontmatter YAML
- As notas de tarefas, projetos ou diários devem conter propriedades estruturadas no cabeçalho (YAML Frontmatter) para rastreabilidade:
  ```yaml
  ---
  projeto_id: proj_001
  projeto_nome: Pagar contas
  data_registro: YYYY-MM-DD
  curva: A
  tags: [pessoal, financeiro]
  status: pendente_sincronia
  ---
  ```

### 3. Desenvolver o Sincronizador de Notas Diárias (`Daily Notes`)
- Criar a função que gera ou adiciona seções no arquivo `YYYY-MM-DD.md` do Obsidian.
- Adicionar:
  - Resumo de tarefas concluídas e pendentes da Curva A.
  - Resultados e percentuais de conclusão das microrrotinas.
  - Desabafo transcrito e insights processados pela IA (Seção *"O que aconteceu"*, *"O que foi excelente"*, *"O que fica de lição"*).

---

## 🧪 Critérios de Aceitação / Validação
- Executar o script `vault_sync.py` deve ler os novos registros da tabela `itens_segundo_cerebro` com status `'pendente_sincronia'` e gerar/atualizar o arquivo Markdown correspondente no Obsidian.
- O status do registro no SQLite deve mudar para `'sincronizado_obsidian'` após o sucesso da escrita.
- O frontmatter do arquivo Markdown gerado no Obsidian deve ser perfeitamente lido e interpretável pelo Obsidian (propriedades válidas).
