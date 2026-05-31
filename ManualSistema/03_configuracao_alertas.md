# 📋 3. Guia de Configuração de Alertas e Lembretes

Para manter você no rumo ao longo do dia, o sistema possui uma infraestrutura ativa de **Alertas e Lembretes automatizados via Telegram**. Eles são alimentados de forma dinâmica pelo banco de dados PostgreSQL (NocoDB) e despachados pelo robô em segundo plano.

---

## 🛠️ Estr Estrutura de Cadastro de Alertas (`TelegramLembretes`)

No NocoDB, você gerencia e cria seus lembretes usando as seguintes colunas obrigatórias e opcionais:

| Nome da Coluna | Tipo | Obrigatório? | Descrição / Opções de Preenchimento |
| :--- | :---: | :---: | :--- |
| **`hora_`** | Time | **Sim** | Horário de envio (formato `HH:MM`, ex: `08:00`, `14:30`). |
| **`mensagem_`** | Text | **Sim** | Texto do alerta (suporta formatação Markdown do Telegram). |
| **`ativo_`** | Text | Não | `Sim` / `Não` (ou em branco para Ativo). |
| **`tipo_lembrete`** | Text | Não | Classificação visual do alerta (determina o emoji). |
| **`frenquecia_disparo`** | Text | Não | Agenda de dias da semana (ou em branco para "todo dia"). |

---

## 🏷️ 1. Como usar o `tipo_lembrete` (Emojis Automáticos)

A coluna `tipo_lembrete` altera automaticamente o emoji e o título da mensagem que você recebe no Telegram. As opções mapeadas no script do robô são:

* **`lembrete`** ou **`lembrate`**  
  * **Visual no Telegram:** 🔔 *Lembrete:* `<sua mensagem>`  
  * *Uso:* Tarefas rápidas e soltas do dia a dia.
* **`Compromisso`**  
  * **Visual no Telegram:** 📅 *Compromisso:* `<sua mensagem>`  
  * *Uso:* Reuniões com terceiros, consultas, datas fixas e inegociáveis.
* **`Rotina`**  
  * **Visual no Telegram:** 🔄 *Rotina:* `<sua mensagem>`  
  * *Uso:* Hábitos estruturados, viradas de bloco de trabalho, autocuidado.
* **Qualquer outro texto** (ex: `Finanças`, `Urgente`)  
  * **Visual no Telegram:** 💡 *[Texto digitado]:* `<sua mensagem>`

---

## 🔄 2. Como usar a `frenquecia_disparo` (A Grafia Correta)

A coluna `frenquecia_disparo` (mantida com esta grafia de banco) controla o cronograma:

* **Todo dia (Padrão)**: Deixe a coluna **vazia/nula**. O lembrete rodará todos os dias.
* **Lembrete Único (`unico`)**: O robô envia a mensagem uma vez e, imediatamente, **desativa** o registro mudando a coluna `ativo_` para `Não` de forma automática.
* **Dias de semana (`seg a sext`)**: Dispara apenas de segunda a sexta-feira.
* **Dias específicos da semana**: Digite o dia abreviado ou por extenso (ex: `segunda`, `quarta-feira`, `dom`). Você também pode digitar múltiplos dias separados por vírgula (ex: `segunda, quarta, sexta`).

---

## 🚀 Proposta de Melhoria Operacional: Integrando Compromissos e Alertas Fixos

Para blindar suas obrigações inegociáveis (como pagamento de contas e mercado), a melhor abordagem é **cadastrá-las diretamente no NocoDB como `Compromisso` na tabela de lembretes**.

### Exemplo de Configurações Recomendadas para sua Grade:

| Hora | Mensagem | Tipo de Lembrete | Frequência Disparo | Justificativa / Filosofia |
| :---: | :--- | :---: | :---: | :--- |
| `08:00` | 💳 **Dia de pagar contas!** Abra o app do banco e quite tudo hoje. Sem desculpas. | `Compromisso` | `unico` ou dias fixos | Obrigações financeiras que exigem integridade. |
| `17:00` | 🛒 **Hora de ir ao mercado!** Desconecte, pegue as sacolas e vá buscar os itens da lista. | `Compromisso` | `sexta` | Bloqueia a agenda no fim do dia de forma fixa. |
| `09:00` | 🧭 **Revisão da Semana (Domingo)**: Reserve 1 hora inteira para planejar a semana com o Coordenador. | `Compromisso` | `domingo` | O ritual inegociável de 1 hora no domingo. |
