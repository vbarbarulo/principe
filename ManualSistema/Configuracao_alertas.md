# 📋 3. Guia de Configuração de Alertas e Lembretes (100% Local)

Para manter você no rumo ao longo do dia e blindar a sua integridade pessoal, o seu sistema utiliza uma grade de **Alertas e Lembretes automatizados via Telegram**. O robô em Python rodando em segundo plano lê diretamente a tabela local Markdown oficial para disparar os envios, sem a necessidade de bancos de dados externos.

---

## 🛠️ A Grade Oficial de Alertas (`Configuracao_Alertas.md`)

Todos os seus lembretes e programações de check-ins ativos estão cadastrados na tabela oficial local em:
👉 [[Configuracao_Alertas]]

### Estrutura Obrigatória da Tabela:

| Coluna | Obrigatória? | O que preencher? | Exemplos / Regras |
| :--- | :---: | :--- | :--- |
| **`Horário`** | **Sim** | Formato de 24h `HH:MM`. | `08:00`, `14:30`, `22:00` |
| **`Categoria`** | **Sim** | Esfera de atuação do alerta. | `Profissional` ou `Pessoal` |
| **`Tipo de Alerta`** | **Sim** | Categoria funcional (determina a intenção). | `Lembrete`, `Compromisso` ou `Rotina` |
| **`Frequência`** | **Sim** | Cronograma de dias de envio. | `seg a sex`, `domingo`, `todo dia`, `unico` |
| **`Status`** | **Sim** | Se o robô deve ou não disparar o envio. | `Ativo` ou `Inativo` |
| **`Evento / Mensagem`** | **Sim** | O texto exato (com emojis e markdown) enviado ao Telegram. | *"Vini, hora de pagar contas!"* |

---

## 🤖 1. Os Três Tipos de Alertas (Como o Robô se Comunica)

O robô lê a coluna **`Tipo de Alerta`** e adiciona automaticamente um prefixo visual de destaque no Telegram:

* **`Lembrete`**:
  * **Visual no Telegram:** 🔔 *Lembrete:* `<sua mensagem>`
  * *Filosofia:* Puxões de orelha horários e checagem de foco.
* **`Compromisso`**:
  * **Visual no Telegram:** 📅 *Compromisso:* `<sua mensagem>`
  * *Filosofia:* Ações com data e hora marcadas inegociáveis.
* **`Rotina`**:
  * **Visual no Telegram:** 🔄 *Rotina:* `<sua mensagem>`
  * *Filosofia:* Viradas de bloco de trabalho, transição familiar de telas e hábitos.

---

## 🚀 2. Prompt de Comando Pronto: Criar & Validar Eventos

Não preencha a tabela Markdown manualmente se não quiser. Você pode pedir para o **Coordenador Interno** ou **Agente Supremo** criar, preencher e validar se está tudo correto de forma 100% segura.

### Prompt de Cópia e Uso (Copy-Paste):

```plaintext
"Antigravity, ative o AGENTE_COORDENADOR.md. Preciso criar um novo alerta/lembrete no meu sistema com os seguintes detalhes:
- Horário: [DIGITE A HORA, ex: 17:30]
- Categoria: [Pessoal ou Profissional]
- Tipo de Alerta: [Lembrete, Compromisso ou Rotina]
- Frequência: [ex: sexta-feira, seg a sex, unico]
- Mensagem: [DIGITE A MENSAGEM DO TELEGRAM COM EMOJIS]

Por favor, faça a validação estrita dos campos: verifique se o horário está no formato HH:MM, se a categoria e tipo estão nas colunas corretas e se a mensagem possui alta integridade e clareza. Estando tudo certo e validado, insira uma nova linha no final da tabela oficial em Configuracao_Alertas.md e me mostre a tabela atualizada para confirmação."
```

Esse prompt garante que o preenchimento seja **pefeito**, livre de erros de digitação e 100% compatível com a leitura automática do robô de Telegram!
