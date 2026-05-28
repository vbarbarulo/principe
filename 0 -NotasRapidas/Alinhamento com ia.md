# Alinhamento de Arquitetura: Automação de Relatórios e Skills Modulares

Este documento serve como um registro do alinhamento técnico para a criação de um sistema de automação de tarefas e revisão diária utilizando Python e Skills (prompts) modulares externas.

---

## 🎯 Objetivo Geral
Criar uma arquitetura onde as regras de negócio, fluxos e orquestração de arquivos fiquem centralizados em scripts **Python**, enquanto as instruções de IA (prompts/skills) fiquem em arquivos **Markdown (.md)** externos. Isso garante independência de ferramentas (como o Antigravity) e facilita a manutenção do comportamento da IA sem alterar código.

---

## 🏗️ Proposta de Arquitetura

A estrutura sugerida para o projeto é a seguinte:

```text
meu-projeto/
├── 0 -NotasRapidas/
│   └── Alinhamento com ia.md       # Este arquivo de notas
├── skills/
│   ├── revisar_dia.md              # Instruções específicas para a revisão diária
│   └── organizar_tarefas.md        # Instruções para categorização de tarefas
├── scripts/
│   ├── auto_reporter.py            # Orquestrador Python principal
│   └── utils.py                    # Funções utilitárias (leitura de arquivos, filtros de data)
└── reports/
    └── diario/                     # Destino dos relatórios gerados automaticamente
```

### Vantagens do Modelo
1. **Portabilidade total**: O fluxo funciona via terminal, WSL, servidores locais ou nuvem.
2. **Reuso direto no Chat**: Se precisar rodar uma skill manualmente, basta referenciar ou colar o conteúdo do arquivo `.md` correspondente no chat do Antigravity.
3. **Desacoplamento**: Ajustes na personalidade ou formato do relatório são feitos no Markdown da skill; ajustes na lógica de leitura e salvamento de arquivos são feitos no Python.

---

## 🛠️ Plano de Implementação

Quando retornarmos, seguiremos os seguintes passos para construir a solução:

### Passo 1: Definição da Skill (`skills/revisar_dia.md`)
Criar o arquivo contendo a persona do agente, o formato esperado do relatório (ex: Resumo Executivo, Tarefas Concluídas, Impedimentos, Próximos Passos) e diretrizes de tom de voz.

### Passo 2: Desenvolvimento do Orquestrador (`scripts/auto_reporter.py`)
Escrever o script em Python que:
- Detecta a data atual.
- Varre a pasta indicada (ex: `0 -NotasRapidas` ou outra pasta de diário) em busca de arquivos criados/modificados no dia.
- Carrega a API do Gemini utilizando a biblioteca oficial `google-genai`.
- Injeta o conteúdo da Skill como `system_instruction`.
- Envia as notas do dia como prompt do usuário.
- Salva a resposta estruturada na pasta de relatórios.

### Passo 3: Agendamento Automático (WSL / Cron)
Configurar uma rotina de execução automática (via `cron` no WSL ou agendador de tarefas) para rodar o script Python no final de cada dia (ex: 18:00 ou 22:00) de forma 100% silenciosa e em segundo plano.

---

## 📝 Exemplo Conceitual do Script Python

```python
import os
from google import genai
from google.genai import types

def carregar_skill(caminho_skill):
    with open(caminho_skill, 'r', encoding='utf-8') as f:
        return f.read()

def executar_automacao():
    # Carrega a skill
    instrucao_ia = carregar_skill("../skills/revisar_dia.md")
    
    # Inicializa o cliente do Gemini
    client = genai.Client()
    
    # Executa a chamada
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Dados coletados hoje...",
        config=types.GenerateContentConfig(
            system_instruction=instrucao_ia,
            temperature=0.2
        )
    )
    
    print("Relatório gerado com sucesso!")

if __name__ == "__main__":
    executar_automacao()
```

---

> ℹ️ **Nota de Retorno:** Quando você estiver pronto para retomar, basta me avisar por onde gostaria de começar! Podemos iniciar criando a estrutura de pastas e a primeira Skill funcional.
