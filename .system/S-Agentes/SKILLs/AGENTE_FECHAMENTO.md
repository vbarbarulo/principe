# 🛠️ Skill Specification: Agente de Fechamento do Dia (v2)

### **Descrição Geral**
Esta Skill é ativada no fim do dia para realizar a consolidação da rotina diária no template do **`diario v2.md`**. Ela evita fluxos cansativos de múltiplas perguntas e respostas. Em vez disso, ela analisa os registros capturados ao longo do dia em `hoje/telegram-YYYY-MM-DD.md` e apresenta um painel contendo apenas o que falta preencher, permitindo que o usuário responda tudo de uma vez.

---

### **1. Como Invocar o Agente**
Para acionar este fluxo, o usuário pode enviar mensagens como:
*   `fechamento do dia`
*   `iniciar fechamento diário`
*   `fechar o dia`

---

### **2. Pipeline de Fechamento (Passo a Passo)**

#### **Fase 1: Leitura do Contexto Diário**
1.  O agente lê o arquivo de logs do dia em `hoje/telegram-YYYY-MM-DD.md` (logs de texto e áudio gerados via Telegram).
2.  Lê o arquivo de template em `c:\principe\ArquivoProcessados\Empresas\ViniciusPessoal\Operações Pessoais\System\Modelos\diario v2.md`.
3.  Preenche automaticamente todos os dados possíveis que foram relatados no log do dia (reuniões, tarefas feitas, pensamentos livres, sentimentos).

#### **Fase 2: O Painel de Perguntas do Fechamento**
O agente apresenta uma resposta estruturada no chat contendo:
1.  **Resumo do que já foi capturado e pré-preenchido** (para validação rápida do usuário).
2.  **O Bloco de Perguntas Pendentes** em formato de lista Markdown limpa para que o usuário copie, responda tudo de uma vez e envie de volta.

As perguntas principais baseadas no `diario v2.md` são:
```markdown
### 📝 Fechamento do Dia — Responda abaixo:

* **1. Título do Dia:** [Insira um título em poucas palavras para resumir o seu dia]
* **2. Nota do Dia (0 a 10):** [Nota de avaliação do dia]
* **3. O que fez de bom / Conquistas:** [O que foi positivo hoje e que pode ser repetido amanhã]
* **4. Acontecimentos ruins / O que evitar:** [O que deu errado e como pode ser evitado no futuro]
* **5. Gratidão:** [Pelo que você foi grato hoje]
* **6. Acompanhamento de Remédios & Hábitos da Noite:**
  * Laura: [ ]
  * Elo: [ ]
  * Vinicius: [ ]
* **7. Brisa ou Complemento Livre:** [Algum pensamento extra ou desabafo (Abra o seu coração)]
```

#### **Fase 2.5: Verificação de Rotinas por Fluxo Natural (TDAH-Friendly)**
Para evitar questionários exaustivos ou checklists chatos de um a um, o agente analisa as rotinas pendentes no arquivo da nota diária e as agrupa em blocos textuais corridos com perguntas naturais e dinâmicas (ex: *"Na Rotina do Meio Dia: Arrumou o quarto? Dobrou as cobertas, esticou o lençol, varreu, passou pano nos móveis e guardou as roupas jogadas? Arrumou o quarto da Laura?..."*). O usuário pode simplesmente relatar o que foi feito em formato de texto e o agente realiza a marcação de `[x]` automaticamente no arquivo do diário.

#### **Fase 3: Consolidação e Arquivamento**
1.  Após receber o bloco de respostas do usuário, o agente une todos os dados (anotações do dia, respostas do painel e hábitos).
2.  Preenche perfeitamente o template `diario v2.md`.
3.  Gera o arquivo markdown completo e o salva de forma organizada em:
    `c:\principe\ArquivoProcessados\Diario\YYYY-MM-DD.md`
4.  Remove ou limpa o arquivo temporário do dia (`hoje/telegram-YYYY-MM-DD.md`) se solicitado, garantindo que o cofre do dia seguinte inicie limpo.
5.  Envia uma mensagem final elegante celebrando o encerramento do dia com foco em tranquilidade mental (TDAH-friendly).
