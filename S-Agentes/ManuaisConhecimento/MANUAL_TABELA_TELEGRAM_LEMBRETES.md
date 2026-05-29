# 📋 Manual de Organização da Tabela de Lembretes do Telegram

Este manual serve como guia prático para preencher e organizar a tabela **`TelegramLembretes`** no NocoDB/Banco de Dados, garantindo que o Agente do Telegram (`telegram_agent.py`) dispare os alertas exatamente como planejado.

---

## 🛠️ Estrutura de Colunas Disponíveis

A tabela de lembretes é composta pelas seguintes colunas que você deve configurar:

| Nome da Coluna | Tipo de Dado | Obrigatório? | Descrição / Opções de Preenchimento |
| :--- | :---: | :---: | :--- |
| **`hora_`** | Time (`HH:MM`) | **Sim** | O horário em que o lembrete deve disparar (ex: `08:00`, `14:30`). |
| **`mensagem_`** | Text | **Sim** | O texto que será enviado ao seu Telegram. Suporta formatação em Markdown (negrito, itálico, etc.). |
| **`ativo_`** | Text | Não | Define se o lembrete está ativo. Use `Sim`, `true`, `1` ou deixe em **branco** para ativo. Para desativar, use `Não`. |
| **`tipo_lembrete`** | Text | Não | Define a classificação visual e o emoji do alerta. |
| **`frenquecia_disparo`** | Text | Não | Define em quais dias ou circunstâncias o alerta deve disparar. |

---

## 🏷️ 1. Como usar o `tipo_lembrete` (Visual / Emojis)

A coluna `tipo_lembrete` altera automaticamente o cabeçalho e o emoji da mensagem enviada no Telegram, tornando-a mais organizada e rápida de ler.

Você pode preencher com as seguintes opções:

* **`lembrate`** ou **`lembrete`**
  * **Visual no Telegram:** 🔔 *Lembrete:* `<sua mensagem>`
  * *Uso recomendado:* Lembretes rápidos do dia a dia, tarefas gerais.
* **`Compromisso`**
  * **Visual no Telegram:** 📅 *Compromisso:* `<sua mensagem>`
  * *Uso recomendado:* Reuniões, consultas, eventos pontuais ou horários marcados.
* **`Rotina`**
  * **Visual no Telegram:** 🔄 *Rotina:* `<sua mensagem>`
  * *Uso recomendado:* Hábitos recorrentes, check-ins diários, tarefas repetitivas.
* **Qualquer outro texto** (ex: `Urgente`, `Finanças`)
  * **Visual no Telegram:** 💡 *[Texto digitado]:* `<sua mensagem>`

---

## 🔄 2. Como usar a `frenquecia_disparo` (Frequências)

A coluna `frenquecia_disparo` (escrita com essa grafia no banco) define o cronograma de disparos. O agente interpreta o texto digitado seguindo estas regras:

### A. Todo dia (Padrão)
* **Como preencher:** Deixe a coluna **vazia (NULL)**.
* **Comportamento:** O agente irá disparar esse lembrete todos os dias da semana no horário marcado.

### B. Lembrete Único (`unico`)
* **Como preencher:** Digite exatamente **`unico`** (ou `Único`).
* **Comportamento:** O agente dispara o lembrete apenas uma vez. Assim que a mensagem é enviada com sucesso ao Telegram, **o agente desativa automaticamente o lembrete no banco de dados** alterando a coluna `ativo_` para `Não`.

### C. Dias de Semana (`seg a sext`)
* **Como preencher:** Digite **`seg a sext`**, **`seg a sex`** ou **`segunda a sexta`**.
* **Comportamento:** O lembrete só irá disparar nos dias úteis (segunda, terça, quarta, quinta e sexta-feira). Não dispara aos sábados e domingos.

### D. Dias Específicos da Semana
Você pode configurar para disparar apenas em um dia ou em dias específicos separados por vírgula:
* **Dia único:** Digite o nome do dia em português, por extenso ou abreviado (ex: `segunda`, `quarta-feira`, `sábado`, `dom`).
* **Múltiplos dias específicos:** Separe-os por vírgulas.
  * *Exemplo 1:* `segunda, quarta, sexta` (dispara apenas nas segundas, quartas e sextas-feiras).
  * *Exemplo 2:* `sábado, domingo` (ou simplesmente `fim de semana` / `fds`).

---

## 📝 Exemplos de Preenchimento Prático

| Hora | Mensagem | Ativo | Tipo de Lembrete | Frequência Disparo | Comportamento Esperado |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `07:30` | Tomar o remédio diário | `Sim` | `Rotina` | *(vazio)* | Dispara **todos os dias** com o cabeçalho `🔄 Rotina:`. |
| `09:00` | Reunião semanal de alinhamento | `Sim` | `Compromisso` | `segunda` | Dispara **apenas nas segundas-feiras** às 09:00 com o cabeçalho `📅 Compromisso:`. |
| `14:00` | Ligar para o suporte do sistema | `Sim` | `lembrete` | `unico` | Dispara **uma única vez**. Após enviar, o próprio agente muda o ativo para `Não`. |
| `18:00` | Fazer o fechamento do caixa diário | `Sim` | `Rotina` | `seg a sext` | Dispara **apenas de segunda a sexta-feira** com o cabeçalho `🔄 Rotina:`. |
| `10:00` | Treino de pernas da academia | `Sim` | `Rotina` | `terça, quinta, sábado` | Dispara **somente às terças, quintas e sábados**. |
