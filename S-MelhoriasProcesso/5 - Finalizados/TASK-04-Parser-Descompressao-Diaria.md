# 🧠 TASK-04: Parser e Fluxo de Descompressão Diária

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Implementar o fluxo de descompressão ativa de final de dia. O usuário descarrega um texto livre ou áudio transcrito desabafando sobre o dia, e a IA faz perguntas de esclarecimento direcionadas para capturar e registrar hábitos, conquistas, impedimentos e tarefas de forma organizada.

---

## 📂 Arquivos Envolvidos
- [NEW] `src/agents/decompression_agent.py`
- [MODIFY] [bot.py](file:///c:/Users/vinic/OneDrive/Área de Trabalho/meu agente de IA/bot.py)

---

## 📝 Passo a Passo de Execução

### 1. Criar o Agente de Descompressão com Agno (Phidata)
- Desenvolver um agente especializado que processa desabafos de linguagem natural.
- Definir o prompt do agente para:
  - Consumir o texto do desabafo diário do usuário.
  - Avaliar o cumprimento implícito de rotinas (peso mencionado, medicamentos tomados, etc.).
  - Elaborar de 2 a 3 perguntas ativas focadas e diretas caso faltem dados essenciais (ex: *"Você conseguiu tomar o remédio hoje?"* ou *"Qual foi a maior dificuldade do seu dia?"*).

### 2. Integrar com o Fluxo de Mensagens
- Quando o usuário aciona o fluxo `/descomprimir` ou emite um desabafo no horário configurado, iniciar a conversa de descompressão.
- Salvar o histórico das respostas temporariamente até que todas as perguntas-chave sejam respondidas.

### 3. Salvar os Resultados Consolidados
- Assim que o fluxo for concluído, salvar no banco SQLite (`logs_descompressao`) o texto bruto, a análise estruturada da IA e as lições aprendidas/decisões tomadas.

---

## 🧪 Critérios de Aceitação / Validação
- O fluxo de descompressão deve iniciar ao comando do usuário.
- O agente deve ser capaz de extrair tarefas ou notas do desabafo livre.
- Se o usuário não mencionar dados essenciais (como sono ou remédios), a IA deve questioná-lo de forma educada e objetiva.
- Ao final, os dados devem estar perfeitamente formatados e persistidos na tabela do SQLite.
