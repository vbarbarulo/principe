# 🛡️ TASK-12: Scripts de Controle, Reinício e Backups Criptografados

**Status:** 🟥 PENDENTE

---

## 🎯 Objetivo
Desenvolver os utilitários operacionais para garantir a robustez, facilidade de manutenção e segurança das informações pessoais do usuário armazenadas localmente no SQLite, criando scripts para backup, reinício rápido e restauração.

---

## 📂 Arquivos Envolvidos
- [NEW] `scripts/backup.py`
- [NEW] `scripts/reboot.sh`
- [NEW] `scripts/reboot_windows.bat`

---

## 📝 Passo a Passo de Execução

### 1. Desenvolver o Script de Backup Criptografado (`backup.py`)
- Criar script em Python que localiza o banco SQLite `agent.db` e a pasta de configurações.
- Compactar tudo em um arquivo ZIP.
- Fornecer opção de criptografar o arquivo final utilizando uma chave forte de segurança fornecida pelo usuário, gerando o arquivo `.zip.enc` ideal para salvar no GitHub ou na nuvem de forma privada.

### 2. Criar os Scripts de Reinício Rápido (`reboot`)
- Desenvolver scripts simples que detectam processos ativos do `bot.py` em execução, derrubam com segurança (evitando corrupção de escrita no SQLite) e reiniciam a aplicação de imediato.
- Criar a versão `.sh` para rodar na VPS/WSL e a versão `.bat` nativa para o Windows.

---

## 🧪 Critérios de Aceitação / Validação
- Executar o script de backup deve gerar um arquivo compactado protegido na pasta desejada contendo todas as tabelas e configurações estáveis.
- O script de reboot deve fechar o bot graciosamente e reerguê-lo em menos de 10 segundos sem perda de estado.
