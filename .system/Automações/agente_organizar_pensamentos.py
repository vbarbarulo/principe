#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Organização de Pensamentos - Hórus System
Lê o arquivo de logs diários (telegram-YYYY-MM-DD.md), envia para a OpenAI GPT-4o-mini
para categorizar de forma inteligente por temas/projetos, mescla com o arquivo existente
hoje/pensamentos_organizados.md de forma estruturada, e limpa o arquivo de entrada original.
"""

import os
import sys
import datetime
import requests
import json
import shutil

# --- CARREGADOR DE VARIÁVEIS DE AMBIENTE (.env) ---
def load_env():
    """Carrega variáveis de ambiente de um arquivo .env local se existir"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        env_path = os.path.join(current_dir, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return
        current_dir = os.path.dirname(current_dir)

load_env()

# --- CONFIGURAÇÕES ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "hoje"))

def read_file_safe(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def write_file_safe(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def obter_resposta_openai(messages):
    """Envia a solicitação para a API da OpenAI e retorna a resposta"""
    if not OPENAI_API_KEY:
        return "Erro: Chave OPENAI_API_KEY não configurada no .env."
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.2
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=60)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            return f"Erro na API da OpenAI: {res.status_code} - {res.text}"
    except Exception as e:
        return f"Exceção ao chamar OpenAI API: {e}"

def organizar_e_mesclar(novas_notas, organizados_existente):
    """Solicita à IA a categorização e mesclagem inteligente dos pensamentos"""
    prompt = f"""Você é o Assistente Supremo do Hórus System. Sua missão é ler as novas notas diárias brutas, extraídas do log do Telegram do usuário, e organizá-las semanticamente por temas/projetos no arquivo de Pensamentos Organizados.

### Diretrizes de Organização:
1. **Identifique o que é Tarefa, Ideia/Insight ou Reflexão Pessoal**.
2. **Categorize por Temas Relevantes**, por exemplo:
   - 💼 **Trabalho & Projetos** (Futuro Corp, DNA, Recrutamento, Devs de Negócio)
   - 💰 **Financeiro & Orçamento** (Contratos, economia, cancelamentos, investimentos)
   - 🧠 **Comportamento, Hábitos & TDAH** (Foco, técnicas de rotinas, controle de notificações)
   - 🏡 **Pessoal & Relacionamento** (Casamento, Elo, filha Laura, metas de vida, saúde, velório/legado)
   - 🛠️ **Melhorias do Sistema (Hórus/Príncipe)** (Novos agentes, sugestões de automações)
   - 💭 **Brizas & Insights Livres** (Pensamentos profundos, ideias soltas)
3. **Se já houver conteúdo organizado anterior** (fornecido abaixo), você deve **MESCLAR inteligentemente** os novos pensamentos com os já existentes, adicionando novas tarefas/anotações na respectiva categoria de forma limpa, sem apagar o que já estava lá nem duplicar itens idênticos.
4. **Use Markdown Elegante**: Use emojis adequados, bullet points bem definidos (como `- [ ]` para tarefas ou `-` para insights) e subtítulos bonitos.

Aqui estão as **Novas Notas Brutas** do Telegram:
---
{novas_notas}
---

Aqui está o conteúdo atual de **Pensamentos Organizados** existente (se estiver vazio, crie a estrutura do zero):
---
{organizados_existente}
---

Retorne estritamente o conteúdo do arquivo Markdown final perfeitamente formatado, pronto para ser salvo. Não inclua blocos de código markdown como ```markdown no início ou fim da resposta.
"""
    messages = [{"role": "user", "content": prompt}]
    return obter_resposta_openai(messages)

def main():
    print("[*] Iniciando Agente de Organização de Pensamentos...")
    
    if not OPENAI_API_KEY:
        print("[-] Erro: OPENAI_API_KEY não configurada no .env!")
        sys.exit(1)
        
    hoje_str = datetime.date.today().strftime("%Y-%m-%d")
    telegram_file = os.path.join(BASE_DIR, f"telegram-{hoje_str}.md")
    organizados_file = os.path.join(BASE_DIR, "pensamentos_organizados.md")
    
    if not os.path.exists(telegram_file):
        print(f"[-] Arquivo de notas brutas de hoje não encontrado: {telegram_file}")
        sys.exit(0)
        
    novas_notas = read_file_safe(telegram_file).strip()
    
    # Se o arquivo de notas brutas estiver vazio ou só tiver o título inicial
    linhas_notas = [l for l in novas_notas.split("\n") if l.strip()]
    if not novas_notas or len(linhas_notas) <= 2 and "Notas e Lembretes" in novas_notas:
        print("[*] Nenhuma nota nova para processar hoje ou o arquivo está vazio.")
        sys.exit(0)
        
    print(f"[*] Lendo notas brutas de: {telegram_file}")
    print(f"[*] Lendo pensamentos organizados atuais (se houver) de: {organizados_file}")
    
    organizados_existente = read_file_safe(organizados_file).strip()
    
    print("[*] Enviando para a OpenAI categorizar e mesclar...")
    resultado_organizado = organizar_e_mesclar(novas_notas, organizados_existente)
    
    if resultado_organizado.startswith("Erro") or resultado_organizado.startswith("Exceção"):
        print(f"[-] Erro ao processar com IA: {resultado_organizado}")
        sys.exit(1)
        
    # Salva o arquivo de pensamentos organizados
    write_file_safe(organizados_file, resultado_organizado.strip() + "\n")
    print(f"[+] Pensamentos organizados salvos com sucesso em: {organizados_file}")
    
    # Fazer um backup silencioso do arquivo de telegram antes de limpá-lo
    backup_file = telegram_file + ".bak"
    shutil.copy2(telegram_file, backup_file)
    print(f"[+] Backup das notas brutas salvo em: {backup_file}")
    
    # Limpa/Zera o arquivo de logs do telegram mantendo apenas a estrutura inicial
    cabecalho_inicial = f"# Notas e Lembretes de {hoje_str}\n\n"
    write_file_safe(telegram_file, cabecalho_inicial)
    print(f"[+] Arquivo de notas brutas original zerado operacionalmente!")
    print("[+] Processamento concluído com sucesso!")

if __name__ == "__main__":
    main()
