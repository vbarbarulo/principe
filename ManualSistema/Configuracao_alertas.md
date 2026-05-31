# 📋 3. Guia de Configuração de Alertas e Lembretes (100% Local)

Para manter você no rumo ao longo do dia e blindar a sua integridade pessoal, o seu sistema utiliza uma grade de **Alertas e Lembretes automatizados via Telegram**. O robô em Python rodando em segundo plano lê diretamente o arquivo JSON local oficial para disparar os envios, sem a necessidade de bancos de dados externos.

---

## 🛠️ O Arquivo Oficial de Alertas (`alertas_config.json`)

Todos os seus lembretes e programações de check-ins ativos estão cadastrados de forma limpa e estruturada no arquivo JSON local em:
👉 [alertas_config.json](../.system/config/alertas_config.json)

### Estrutura Obrigatória do JSON:

```json
{
  "alertas": [
    {
      "horario": "HH:MM",
      "categoria": "Pessoal" ou "Profissional",
      "tipo": "Lembrete", "Compromisso" ou "Rotina",
      "frequencia": "todo dia", "seg a sex", "domingo", "unico",
      "status": "Ativo" ou "Inativo",
      "mensagem": "Sua mensagem com emojis aqui"
    }
  ]
}
```

---

## 🤖 1. Os Três Tipos de Alertas (Como o Robô se Comunica)

O robô lê a propriedade **`tipo`** e adiciona automaticamente um prefixo visual de destaque no Telegram:

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

Não edite o arquivo JSON manualmente se não quiser correr o risco de quebrar a sintaxe. Você pode pedir para o **Coordenador Interno** ou **Agente Supremo** criar, preencher e validar se está tudo correto de forma 100% segura.

### Prompt de Cópia e Uso (Copy-Paste):

```plaintext
"Antigravity, ative o AGENTE_COORDENADOR.md. Preciso criar um novo alerta/lembrete no meu sistema com os seguintes detalhes:
- Horário: [DIGITE A HORA, ex: 17:30]
- Categoria: [Pessoal ou Profissional]
- Tipo de Alerta: [Lembrete, Compromisso ou Rotina]
- Frequência: [ex: sexta-feira, seg a sex, unico]
- Mensagem: [DIGITE A MENSAGEM DO TELEGRAM COM EMOJIS]

Por favor, faça a leitura de alertas_config.json, insira o novo objeto respeitando as chaves e arrays, valide a formatação do JSON, salve e me exiba o arquivo atualizado para confirmação."
```

Esse prompt garante que o preenchimento seja **perfeito**, livre de erros de digitação e 100% compatível com a leitura automática do robô de Telegram!
