# 🗄️ TASK-02: Refatoração do Banco de Dados SQLite

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Migrar e evoluir o banco de dados `agent.db` existente para contemplar as novas tabelas robustas do ecossistema Hórus (`registros_rotina`, `itens_segundo_cerebro`, `memorias_usuario` e as tabelas nativas de histórico do Agno).

---

## 📂 Arquivos Envolvidos
- [MODIFY] [database.py](file:///c:/Users/vinic/OneDrive/Área de Trabalho/meu agente de IA/database.py)

---

## 📝 Passo a Passo de Execução

### 1. Fazer Backup do banco atual
- Criar rotina de backup preventivo do `agent.db` atual antes de aplicar qualquer script de migração.

### 2. Modificar `database.py`
- Adicionar ou atualizar as definições de tabela para incluir:
  - `registros_rotina`: Armazenará o status diário consolidado das rotinas com chave composta `id` (ex: `'YYYY-MM-DD-rotina_id'`), campos para ações concluídas (JSON), ações puladas (JSON), dados capturados (JSON) e status.
  - `itens_segundo_cerebro`: Armazenará insights temporários classificados por curva ABC, tipo de nota, horizontes de tempo e tags.
  - `memorias_usuario`: Armazenará a memória semântica com campos de `categoria`, `fato` e `importancia` (níveis de 1 a 5).
  - Garantir suporte às tabelas internas do Agno (Phidata) para persistência automática do histórico de chat (`SqlAgentStorage`).

### 3. Criar script de migração segura
- Desenvolver funções que detectam se tabelas antigas contêm dados e migram as tabelas atuais (`checkin_saude`, `rotinas_log`, etc.) de forma a não perder o histórico anterior do usuário.

---

## 🧪 Critérios de Aceitação / Validação
- O arquivo `database.py` deve rodar perfeitamente e inicializar as novas tabelas sem erros.
- A integridade do banco de dados antigo deve ser mantida (nenhum dado histórico de sono/peso deve ser perdido).
- Deve ser possível inserir dados de teste utilizando as chaves compostas na tabela `registros_rotina`.
