# ⚡ TASK-03: Engine de Upsert Inteligente

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Desenvolver a lógica no backend em Python responsável por gerenciar e consolidar o estado de hábitos e rotinas diárias por meio de chaves compostas hash (`data-rotina_id`), evitando registros duplicados no banco SQLite mesmo quando o usuário interage múltiplas vezes no mesmo dia.

---

## 📂 Arquivos Envolvidos
- [NEW] `src/database/upsert_engine.py`
- [MODIFY] [database.py](file:///c:/Users/vinic/OneDrive/Área de Trabalho/meu agente de IA/database.py)

---

## 📝 Passo a Passo de Execução

### 1. Criar `upsert_engine.py`
- Desenvolver funções que recebem a data (ex: `2026-05-27`) e o `rotina_id` (ex: `RM1`).
- Gerar o hash composto primário do registro (ex: `'2026-05-27-RM1'`).

### 2. Implementar a lógica de Mesclagem de Dados (Merge/Upsert)
- Ao receber novas ações concluídas, o sistema deve:
  - Verificar se a linha já existe na tabela `registros_rotina`.
  - Se não existir, executar o `INSERT` inicial.
  - Se já existir, carregar a lista de ações concluídas (`acoes_concluidas`), mesclar sem duplicar usando conjuntos Python (`set`), e atualizar a linha com `UPDATE`.
- Fazer o mesmo fluxo para os campos `acoes_puladas`, `dados_capturados` (como peso do dia) e `observacoes`.

### 3. Calcular Dinamicamente o Status da Rotina
- Baseado nas tarefas listadas em `rotinas.md` para aquele bloco e no total concluído/pulado, computar dinamicamente o status do registro (`completo`, `parcial`, `incompleto`).

---

## 🧪 Critérios de Aceitação / Validação
- O motor de upsert deve garantir que apenas uma linha seja gerada no banco para a combinação única de `data` e `rotina_id`.
- Chamar a função de atualização 5 vezes seguidas adicionando itens concluídos progressivos não deve causar falha de chave primária duplicada e deve consolidar todos os itens concluídos no JSON final.
