# 🛠️ Skill Specification: Agente de Fechamento & Processamento Diário (v2)

### **Descrição Geral**
Esta Skill é ativada no fim do dia (ou sob demanda) para realizar a leitura do contexto diário capturado em `hoje/telegram-YYYY-MM-DD.md`, consolidar a rotina, preencher hábitos e gerar relatórios executivos de suporte ao TDAH de forma leve e modular, sem acumular textos gigantescos em um único arquivo de diário. Ela apresenta um painel contendo apenas o que falta preencher, permitindo que o usuário responda tudo de uma vez.

---

### **1. Como Invocar o Agente**
Para iniciar a sua rotina ou fechamento, basta enviar mensagens como:
* `fechamento do dia`
* `iniciar fechamento diário`
* `fechar o dia`
* `processar minhas notas de hoje`

---

### **2. Pipeline de Processamento & Fechamento (Passo a Passo)**

#### **Fase 1: Leitura do Contexto Diário**
1. O agente lê o arquivo de logs do dia em `hoje/telegram-YYYY-MM-DD.md` (logs de texto e áudio gerados via Telegram).
2. Lê o arquivo de template em `c:\principe\ArquivoProcessados\Empresas\ViniciusPessoal\Operações Pessoais\System\Modelos\diario v2.md`.
3. Preenche automaticamente todos os dados possíveis que foram relatados no log do dia (reuniões, tarefas feitas, pensamentos livres, sentimentos).

#### **Fase 2: O Painel de Perguntas do Fechamento**
O agente apresenta uma resposta estruturada no chat contendo:
1. **Resumo do que já foi capturado e pré-preenchido** (para validação rápida do usuário).
2. **O Bloco de Perguntas Pendentes** em formato de lista Markdown limpa para que o usuário copie, responda tudo de uma vez e envie de volta.

As perguntas principais baseadas no `diario v2.md` são:
```markdown
### 📝 Fechamento do Dia — Responda abaixo:

* **1. Título do Dia:** [Insira um título em poucas palavras para resumir o seu dia]
* **2. Nota do Dia (0 a 10):** [Nota de avaliação do dia]
* **3. O que fez de bom / Conquistas:** [O que foi positivo hoje e que pode ser repetido amanhã]
* **4. Acontecimentos ruins / O que evitar:** [O que deu errado e como pode ser evitado no futuro]
* **5. Gratidão:** [Pelo que você foi grato hoje]
* **6. Fator Confiabilidade & Propósito:**
  * De 0 a 10, o quanto você foi confiável com os seus compromissos hoje? [Nota]
  * O que você executou hoje que está diretamente alinhado com o seu "Porquê" de longo prazo (Família, Saúde, R$ 4M)? [Resposta]
  * Quais hábitos do empilhamento foram validados com sucesso hoje? [Resposta]
* **7. Acompanhamento de Remédios & Hábitos da Noite:**
  * Laura: [ ]
  * Elo: [ ]
  * Vinicius: [ ]
* **8. Brisa ou Complemento Livre:** [Algum pensamento extra ou desabafo (Abra o seu coração)]
```

#### **Fase 2.5: Verificação de Rotinas por Fluxo Natural (TDAH-Friendly)**
Para evitar questionários exaustivos ou checklists chatos de um a um, o agente analisa as rotinas pendentes no arquivo da nota diária e as agrupa em blocos textuais corridos com perguntas naturais e dinâmicas (ex: *"Na Rotina do Meio Dia: Arrumou o quarto? Dobrou as cobertas, esticou o lençol, varreu, passou pano nos móveis e guardou as roupas jogadas? Arrumou o quarto da Laura?..."*). O usuário pode simplesmente relatar o que foi feito em formato de texto e o agente realiza a marcação de `[x]` automaticamente no arquivo do diário.

---

### **3. Fase 3: Consolidação e Arquivamento Modular**
Após receber o bloco de respostas do usuário, o agente une todos os dados (anotações do dia, respostas do painel e hábitos), cria uma pasta dedicada com o nome no formato `ano-mes-dia` (ex: `c:\principe\ArquivoProcessados\Relatórios\YYYY-MM-DD\`) e divide o conteúdo salvando 7 arquivos individuais organizados por tema dentro dela:

1. **`telegram-YYYY-MM-DD.md`**: O histórico bruto de tudo que foi conversado/anotado no dia via Telegram (mantendo o texto original completo para futuras análises).
2. **`Pessoal-YYYY-MM-DD.md`**: Brisas de sentimentos, dinâmica de casal, reflexões pessoais íntimas, pets e desabafos sobre o quintal/casa.
3. **`Trabalho-YYYY-MM-DD.md`**: Desafios de produtividade, progresso dos OKRs, reuniões profissionais (ex: com Jesus, Igor), motivadores/desmotivadores da Futuro Corp.
4. **`Rotina-YYYY-MM-DD.md`**: Tracker de hábitos completo (sono, acordar, peso, checklist de remédios da Laura, Elo e Vinícius, consumo de água, digestivo e ciclo).
5. **`Organizado-YYYY-MM-DD.md`**: Logs processados e marcação das atividades macros que de fato aconteceram.
6. **`Planejamento-YYYY-MM-DD.md`**: Sonhos estruturados, missões de 10 anos, metas de 90 dias, e cartas de compromisso geradas ou lidas no dia.
7. **`Melhorias-YYYY-MM-DD.md`**: Ideias de melhorias, novos agentes, bugs, erros identificados ou especificações sobre a evolução do próprio sistema Príncipe capturados durante o dia (para análises e implementações futuras).

---

### **4. Outputs (Saídas Finais)**
* **Nota Diária Final (Relatório Executivo + Diário Pessoal + Tracker)** salva em `/ArquivoProcessados/Diario/YYYY-MM-DD.md`.
* **Atualização do Painel da Semana**: O agente sincroniza a conclusão dos hábitos e metas de comportamento na nota da semana correspondente em `c:\principe\ArquivoProcessados\Diario\Semana\YYYY-W[WW].md`.
* **Conjunto de 7 Relatórios Modulares Diários** salvos na subpasta `c:\principe\ArquivoProcessados\Relatórios\YYYY-MM-DD\`.
* Remocão/arquivamento do arquivo ativo do dia (`hoje/telegram-YYYY-MM-DD.md`) garantindo limpeza operacional após a consolidação segura do histórico no diretório final.
* **Notificação Executiva** despachada para o Telegram celebrando o encerramento do dia com foco em tranquilidade mental (TDAH-friendly).
