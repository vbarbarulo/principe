# 🛠️ Skill Specification: Agente de Fechamento & Processamento Diário (v4)

### **Descrição Geral**
Esta Skill é ativada no fim do dia (ou sob demanda) para realizar a leitura do contexto diário capturado em `hoje/telegram-YYYY-MM-DD.md`, consolidar a rotina, preencher hábitos, conduzir a avaliação do **Criteriómetro Límbico** e a rotina da **Roda da Vida**, e salvar os dados de forma 100% modular nos novos caminhos de `ArquivoProcessados/`.

---

### **1. Como Invocar o Agente**
Para iniciar a sua rotina ou fechamento, basta enviar mensagens como:
*   `fechamento do dia`
*   `iniciar fechamento diário`
*   `fechar o dia`
*   `processar minhas notas de hoje`

---

### **2. Pipeline de Processamento & Fechamento (Passo a Passo)**

#### **Fase 1: Leitura do Contexto Diário**
1. O agente lê o arquivo de logs do dia em `hoje/telegram-YYYY-MM-DD.md`.
2. Lê a base inalterável de identidade em [ArquivoProcessados/IdentidadeRaiz/Base_Identidade_Vida.md](file:///c:/principe/ArquivoProcessados/IdentidadeRaiz/Base_Identidade_Vida.md).
3. Preenche automaticamente todos os dados possíveis que foram relatados no log do dia (reuniões, tarefas feitas, pensamentos livres, sentimentos).

#### **Fase 2: O Painel de Perguntas do Fechamento (Com Criteriómetro & Roda da Vida)**
O agente apresenta uma resposta estruturada contendo as perguntas pendentes:

```markdown
### 📝 Fechamento do Dia — Responda abaixo:

* **1. Título do Dia:** [Insira um título em poucas palavras para resumir o seu dia]
* **2. Nota do Dia (0 a 10):** [Nota de avaliação do dia]
* **3. O que fez de bom / Conquistas:** [O que foi positivo hoje e que pode ser repetido amanhã]
* **4. Acontecimentos ruins / O que evitar:** [O que deu errado e como pode ser evitado no futuro]
* **5. Gratidão:** [Pelo que você foi grato hoje]
* **6. Fator Confiabilidade (Brené Brown) & Criteriómetro de Triagem Emocional/Operacional:**
  * De 0 a 10, o quanto você foi de fato confiável com as promessas que fez a si mesmo hoje? [Nota]
  * Você conseguiu proteger e executar a sua **Única Coisa** da Curva A hoje? [Sim / Não]
  * Houve alguma meta, sonho ou brisa analisada hoje pelo Criteriómetro? Se sim, qual foi a pontuação detalhada? (Alinhamento Ciclo: X, Blindagem Familiar: Y, Clareza Operacional: Z, Integridade/Confiabilidade: W. Total: Nota/10) [Resposta]
  * Algum item foi adicionado à *Quarentena de 14 Dias* em [Gestao_Compras.md](file:///c:/principe/ArquivoProcessados/PlanejamentoEstrategico/Gestao_Compras.md) hoje para segurar a impulsividade? [Sim / Não / Item]
  * Quantas tarefas inúteis ou "voadoras" (Quadrantes III/IV) você barrou com o Criteriómetro e mandou para a Caixa de Entrada de `💭 Sonhos.md`? [Resposta]
* **7. Acompanhamento de Remédios & Hábitos da Noite:**
  * Laura: [ ]
  * Elo: [ ]
  * Vinicius: [ ]
* **8. 🧭 Check-in da Roda da Vida & Auditoria de Compras (Apenas nos Domingos):**
  * *Saúde:* De 0 a 10, como avalia sua energia física, treinos e alimentação esta semana? [Nota]
  * *Família:* De 0 a 10, quanto você conseguiu desligar o modo de produção de trabalho e estar 100% presente com a Laura e a Elo sem telas? [Nota]
  * *Finanças & Compras:* De 0 a 10, como avalia a Operação Trincheira? Você auditou a sua listagem em [Gestao_Compras.md](file:///c:/principe/ArquivoProcessados/PlanejamentoEstrategico/Gestao_Compras.md) com o **Diretor de Crise** hoje para liberar itens essenciais (ex: tênis) ou barrar/limpar os itens de quarentena? [Resposta]
* **9. Brisa ou Complemento Livre (Direcionado ao arquivo Pessoal-YYYY-MM-DD.md):** [Abra o seu coração: desabafo de relacionamentos, gatilhos de injustiça ou comparação que enfrentou hoje]
```

---

### **3. Fase 3: Consolidação e Técnica de Ajuste de Margem Semântica**

#### 📌 Regra de Ajuste Semântico Incremental & Score de Confiabilidade
O agente **NUNCA** irá sobrescrever ou recriar do zero o arquivo de identidade em [Base_Identidade_Vida.md](file:///c:/principe/ArquivoProcessados/Empresas/ViniciusPessoal/Base_Identidade_Vida.md).
*   Toda vez que identificar um padrão de alta relevância (ex: decisões consistentes de proteção à família, controle bem-sucedido de gatilhos ou avanços reais de identidade) pontuado com nota **8.0 a 10** no Criteriómetro, o agente abrirá a nota e adicionará incrementalmente no final do arquivo:
    ```markdown
    ### 📌 Insight Arqueológico Extraído em YYYY-MM-DD
    *   **Contexto:** [Resumo breve do padrão observado e gatilho associado]
    *   **Aprendizado Límbico:** [Identidade e Eco extraído, aplicando o Protocolo Protetor]
    ```
*   **Computação de Confiabilidade Pessoal:** O agente calcula e registra um score de confiabilidade de 0 a 10 (baseado na autodeclaração do usuário e na entrega inegociável da sua **Única Coisa**).

#### 📂 Arquivamento Físico e Modular
O agente divide os dados coletados e grava nos seguintes caminhos de `c:/principe/ArquivoProcessados/`:

1.  **Identidade e Ciclos Estratégicos:**
    *   `Empresas/ViniciusPessoal/Base_Identidade_Vida.md` -> Ajustes semânticos de princípios e identidade descritos acima.
    *   `Empresas/ViniciusPessoal/Protocolos_Comportamentais.md` -> Calibração e regras algorítmicas de contenção de estresse/hiperfoco.
    *   `PlanejamentoEstrategico/Diretriz_10_Anos.md` -> A Estrela do Norte macro.
    *   `PlanejamentoEstrategico/Plano_5_Anos.md` -> A ponte de transição.
    *   `PlanejamentoEstrategico/Plano_1_Ano.md` -> Objetivos do ano.
    *   `PlanejamentoEstrategico/Caverna_Trimestral.md` -> Foco de 90 dias (Projeto DNA/Sobrevivência).
2.  **Históricos de Curto Prazo (Diários e Semanais):**
    *   `Diario/Semana/` -> Metas de 1 semana e retrospectiva da Roda da Vida (Domingos).
    *   `Diario/Mes/` -> Alinhamento tático de meses e Cavernas.
    *   `Relatorios/YYYY-MM-DD/Pessoal-YYYY-MM-DD.md` -> Registro limpo e autocontido de desabafos pessoais, sentimentos e relacionamentos, livre de dados operacionais e de trabalho.
    *   `Relatorios/YYYY-MM-DD/Planejamento-YYYY-MM-DD.md` -> Insight ou meta pontuada que altera as camadas superiores.
    *   `Relatorios/YYYY-MM-DD/` -> Gravação dos relatórios modulares diários (telegram, pessoal, trabalho, rotina, organizado, planejamento, melhorias).

O agente realiza a exportação ativa de um compilado das dores da semana de 'Pessoal' e 'Trabalho' nas sextas-feiras/fins de semana, servindo como o input primário imediato para as perguntas do [AGENTE_TERAPEUTA.md](file:///c:/principe/.system/S-Agentes/SKILLs/AGENTE_TERAPEUTA.md) no Sábado de manhã.

Após a consolidação segura, o agente deleta o arquivo provisório `hoje/telegram-YYYY-MM-DD.md` mantendo o ecossistema limpo e focado.
