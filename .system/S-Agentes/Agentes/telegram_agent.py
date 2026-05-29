#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Agent - Hórus System
Agente que escuta mensagens do usuário via Telegram, salva logs em arquivos diários Markdown,
e gerencia o envio de lembretes programados ao longo do dia."""

import os
import sys
import json
import time
import datetime
import threading
import requests
import psycopg2

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

# --- AUXILIAR DE CAMINHO PARA COMPATIBILIDADE WINDOWS/WSL ---
def regularize_path(path):
    """Converte caminhos do WSL (/mnt/c/...) para caminhos do Windows se estiver no Windows"""
    if sys.platform == 'win32' or os.name == 'nt':
        if path.startswith('/mnt/c/'):
            return path.replace('/mnt/c/', 'C:/', 1)
    return path

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_DIR = regularize_path('/mnt/c/principe/hoje')
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_agent_state.json')

TEMPLATE_PATH = regularize_path("/mnt/c/principe/1-OrganizaçãoManual/-/Diario/diario v2.md")
DIARIO_DIR = regularize_path("/mnt/c/principe/1-OrganizaçãoManual/-/Diario")

def read_file_safe(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def obter_resposta_openai(messages):
    """Envia o histórico de mensagens para a API da OpenAI e retorna a resposta"""
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
        "temperature": 0.3
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=60)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            print(f"[-] Erro OpenAI API: {res.status_code} - {res.text}")
            return f"Erro na API da OpenAI: {res.text}"
    except Exception as e:
        print(f"[-] Exceção ao chamar OpenAI API: {e}")
        return f"Exceção ao chamar OpenAI API: {e}"

def get_system_prompt_relatorio(hoje, notas_dia, template_content):
    return f"""Você é o Assistente Horus, um organizador pessoal focado em alto desempenho.
O seu objetivo é ajudar o usuário a montar o seu Relatório Diário de hoje ({hoje}) com base no template 'diario v2.md' fornecido abaixo.

Ao longo do dia, o usuário registrou algumas notas rápidas. Use-as para preencher o máximo de informações possível do template.

Aqui estão as notas registradas hoje pelo usuário:
---
{notas_dia}
---

Aqui está o template 'diario v2.md' que você deve preencher:
---
{template_content}
---

Instruções para o diálogo:
1. Analise o que já pode ser preenchido do template com base nas notas do dia.
2. Identifique os campos que ainda estão vazios ou incompletos (por exemplo: notas do sono, peso, respostas sobre o compromisso diário, prioridades, checklist de ações macro com o 'Feito %' e 'Tempo gasto minutos', etc.).
3. Em cada interação:
   - Apresente um resumo muito breve do progresso do preenchimento ou mostre o que já preencheu.
   - Faça perguntas claras e curtas para obter as informações que faltam. **Pergunte apenas uma ou duas coisas por vez** para não sobrecarregar o usuário.
   - Seja encorajador, prático e converse de forma amigável em português (pt-br).
4. Se o usuário digitar '/salvar' ou você identificar que todas as perguntas fundamentais foram respondidas e o relatório está completo, gere o arquivo final do relatório diário perfeitamente preenchido em formato Markdown e finalize a sua resposta com a tag especial: `[CONCLUIDO]`. Após a tag, exiba apenas o conteúdo markdown final do relatório para que o sistema possa salvá-lo automaticamente.
"""

# --- GERENCIADOR DE BLOCOS DE CONTEÚDO (LONGOS / ARQUIVOS) ---
def dividir_texto_em_blocos(texto):
    """Usa OpenAI para dividir um texto longo em blocos lógicos autônomos"""
    if not OPENAI_API_KEY:
        return [texto]
        
    prompt = f"""Analise o texto a seguir e divida-o em blocos lógicos autônomos.
Cada bloco deve representar uma única unidade de informação (uma tarefa específica, uma anotação, um pensamento sobre um projeto, etc.).
Retorne a resposta estritamente no formato de uma lista JSON de strings, como no exemplo:
["bloco 1", "bloco 2"]

Texto para divisão:
{texto}
"""
    try:
        res = obter_resposta_openai([{"role": "user", "content": prompt}])
        # Limpa blocos de código
        if res.startswith("```json"):
            res = res[7:].strip()
        elif res.startswith("```"):
            res = res[3:].strip()
        if res.endswith("```"):
            res = res[:-3].strip()
            
        return json.loads(res)
    except Exception as e:
        print(f"[-] Erro ao dividir texto em blocos: {e}")
        # Fallback por quebras de linha duplas se falhar
        return [b.strip() for b in texto.split("\n\n") if b.strip()]

def analisar_bloco(bloco_texto, empresas_config):
    """Classifica o bloco como Tarefa ou Nota e tenta inferir Empresa/Departamento/Projeto"""
    if not OPENAI_API_KEY:
        return {"classe": "desconhecido", "empresa": None, "departamento": None, "projeto": None, "titulo": "Nota"}
        
    prompt = f"""Analise o bloco de texto a seguir e classifique-o.
Classificações possíveis:
1. "tarefa" (se descreve uma ação clara a ser executada, um checklist, um TODO).
2. "nota" (se for uma reflexão, anotação de reunião, informação útil, pensamento, etc.).

Se for "nota", tente mapear para uma Empresa, Departamento e Projeto cadastrados na nossa estrutura padrão.

Aqui está a nossa estrutura padrão de Empresas, Departamentos e Projetos:
{json.dumps(empresas_config, indent=2, ensure_ascii=False)}

Tente encontrar a melhor correspondência. Se não encontrar uma correspondência exata, tente inferir a Empresa, Departamento e Projeto mais adequados baseados no contexto do texto.
Gere também um "titulo" curto e adequado para a nota se for salva como arquivo.

Retorne estritamente um objeto JSON no seguinte formato:
{{
  "classe": "tarefa" ou "nota",
  "confianca_classe": 0.0 a 1.0,
  "empresa": "Nome da Empresa ou null",
  "departamento": "Nome do Departamento ou null",
  "projeto": "Nome do Projeto ou null",
  "titulo": "Título curto para a nota ou null"
}}

Bloco de texto:
---
{bloco_texto}
---
"""
    try:
        res = obter_resposta_openai([{"role": "user", "content": prompt}])
        if res.startswith("```json"):
            res = res[7:].strip()
        elif res.startswith("```"):
            res = res[3:].strip()
        if res.endswith("```"):
            res = res[:-3].strip()
            
        return json.loads(res)
    except Exception as e:
        print(f"[-] Erro ao analisar bloco: {e}")
        return {"classe": "desconhecido", "empresa": None, "departamento": None, "projeto": None, "titulo": "Nota"}

def adicionar_tarefa_nocodb(texto_tarefa):
    """Insere uma tarefa diretamente no banco de dados NocoDB"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        sql = """
            INSERT INTO p72a9cobkwj7ta3."Tarefas" 
            ("Tarefa", "Status", "Prioridade", "DT_inicio", "ano", "M_s", "tipo_tarefa", "Projetos", "execu__o_") 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        hoje = datetime.date.today()
        ano = str(hoje.year)
        mes = str(hoje.month).zfill(2)
        data_inicio = hoje.strftime('%Y-%m-%d')
        
        cur.execute(sql, (
            texto_tarefa,
            'Em Aberto',
            'p4',
            data_inicio,
            ano,
            mes,
            'TAREFA',
            '📦 Caixa de Entrada',
            '00 - Nova Tarefa'
        ))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"[-] Erro ao salvar tarefa no banco: {e}")
        return False
    finally:
        if conn:
            conn.close()

def salvar_nota_estruturada(texto, empresa, departamento, projeto, titulo):
    """Salva um bloco de anotação na pasta correspondente de organização"""
    base_org = regularize_path("/mnt/c/principe/1-OrganizaçãoManual/Empresas")
    
    # Garante valores padrões se vierem vazios
    emp = empresa or "ViniciusPessoal"
    dept = departamento or "Operações Pessoais"
    proj = projeto or "Z-brisas"
    tit = titulo or f"Nota-{datetime.datetime.now().strftime('%H%M%S')}"
    
    # Limpa caracteres inválidos para nome de arquivo
    tit_limpo = "".join(c for c in tit if c.isalnum() or c in (' ', '_', '-')).strip()
    if not tit_limpo:
        tit_limpo = "Nota-Sem-Titulo"
        
    diretorio = os.path.join(base_org, emp, dept, proj)
    os.makedirs(diretorio, exist_ok=True)
    
    filepath = os.path.join(diretorio, f"{tit_limpo}.md")
    
    # Se o arquivo já existir, incrementamos o nome
    contador = 1
    while os.path.exists(filepath):
        filepath = os.path.join(diretorio, f"{tit_limpo}_{contador}.md")
        contador += 1
        
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {tit}\n\n")
            f.write(f"**Data:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Empresa:** {emp} | **Departamento:** {dept} | **Projeto:** {proj}\n\n")
            f.write("---\n\n")
            f.write(texto)
        return filepath
    except Exception as e:
        print(f"[-] Erro ao salvar nota estruturada: {e}")
        return None

def processar_proximo_bloco(token, chat_id, state):
    """Lê o próximo bloco pendente, analisa com a IA e pergunta ao usuário como deseja salvar"""
    idx = state.get("bloco_index", 0)
    blocos = state.get("blocos", [])
    
    if idx >= len(blocos):
        # Finalizou todos os blocos!
        state["processando_blocos"] = False
        state["blocos"] = []
        state["bloco_index"] = 0
        save_state(state)
        send_telegram_message(token, chat_id, "✅ *Todos os blocos do arquivo/texto foram processados com sucesso!*")
        return
        
    bloco = blocos[idx]
    texto_bloco = bloco["texto"]
    
    # Carrega as configurações de empresas
    empresas_config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'empresas_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                empresas_config = json.load(f)
        except Exception as e:
            print(f"[-] Erro ao ler empresas_config.json: {e}")
            
    # Analisa o bloco com OpenAI
    analise = analisar_bloco(texto_bloco, empresas_config)
    bloco["analise"] = analise
    save_state(state)
    
    classe = analise.get("classe", "desconhecido")
    
    prompt_mensagem = (
        f"📦 *Processando Bloco {idx + 1} de {len(blocos)}:*\n"
        f"```\n{texto_bloco}\n```\n"
        f"💡 *Sugestão da IA:*\n"
    )
    
    if classe == "tarefa":
        prompt_mensagem += f"👉 *Tarefa* (inserir no NocoDB)\n\n"
    else:
        emp = analise.get("empresa", "ViniciusPessoal")
        dept = analise.get("departamento", "Operações Pessoais")
        proj = analise.get("projeto", "Z-brisas")
        tit = analise.get("titulo", "Nota")
        prompt_mensagem += (
            f"👉 *Nota de Texto*\n"
            f"🏢 Empresa: `{emp}`\n"
            f"📁 Depto: `{dept}`\n"
            f"📂 Projeto: `{proj}`\n"
            f"📝 Título sugerido: `{tit}`\n\n"
        )
        
    prompt_mensagem += (
        "Como deseja salvar?\n\n"
        "1️⃣ Enviar como *Tarefa* para o NocoDB\n"
        "2️⃣ Salvar como *Nota* (confirma os dados sugeridos acima)\n"
        "3️⃣ Alterar manualmente (Responda: `nota Empresa, Departamento, Projeto, Título`)\n"
        "4️⃣ Pular este bloco (Responda: `4` ou `pular`)"
    )
    
    send_telegram_message(token, chat_id, prompt_mensagem)


# Banco de dados
DB_HOST = os.getenv('DB_HOST', '89.116.214.181')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'nocodb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'i8PvK1TUvfmKhYasSMLE')

# --- TRANSCRIÇÃO DE ÁUDIO VIA WHISPER ---
def transcrever_audio(token, file_id):
    """Obtém o caminho do arquivo de áudio no Telegram, faz o download e transcreve usando OpenAI Whisper API"""
    if not OPENAI_API_KEY:
        print("[-] Erro: OPENAI_API_KEY não está configurada!")
        return "[Erro: Chave do OpenAI não configurada]"
    
    try:
        # 1. Obter caminho do arquivo via API do Telegram
        url_file_info = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
        res = requests.get(url_file_info, timeout=15).json()
        if not res.get("ok"):
            print("[-] Falha ao obter informações do arquivo no Telegram.")
            return "[Erro ao obter arquivo no Telegram]"
            
        file_path = res["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        
        # 2. Fazer o download do arquivo de áudio
        print(f"[*] Fazendo download do áudio de: {download_url}")
        audio_content = requests.get(download_url, timeout=30).content
        
        # 3. Salvar temporariamente
        temp_filename = f"temp_voice_{file_id}.oga"
        temp_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), temp_filename)
        with open(temp_filepath, "wb") as f:
            f.write(audio_content)
            
        # 4. Transcrever via Whisper API
        print("[*] Enviando áudio para transcrição via OpenAI Whisper...")
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        with open(temp_filepath, "rb") as audio_file:
            files = {
                "file": (temp_filename, audio_file, "audio/ogg"),
                "model": (None, "whisper-1")
            }
            res_whisper = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                timeout=60
            )
            
        # 5. Remover arquivo temporário
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            
        if res_whisper.status_code == 200:
            transcrito = res_whisper.json().get("text", "")
            print(f"[+] Transcrição concluída: '{transcrito}'")
            return transcrito
        else:
            print(f"[-] Erro na Whisper API: Status {res_whisper.status_code} - {res_whisper.text}")
            return f"[Erro na Whisper API: {res_whisper.text}]"
            
    except Exception as e:
        print(f"[-] Exceção ao transcrever áudio: {e}")
        return f"[Erro inesperado ao transcrever: {e}]"

# --- CONSULTA AO BANCO DE DADOS ---
def get_active_reminders_from_db():
    """Busca os lembretes ativos diretamente do PostgreSQL/NocoDB"""
    reminders = []
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        # Seleciona apenas os ativos e busca os novos campos de tipo e frequência
        cur.execute("""
            SELECT id, hora_, mensagem_, tipo_lembrete, frenquecia_disparo 
            FROM p72a9cobkwj7ta3."TelegramLembretes" 
            WHERE ativo_ IS NULL OR ativo_ IN ('Sim', 'true', '1');
        """)
        rows = cur.fetchall()
        for row in rows:
            r_id = row[0]
            t_val = row[1]
            msg = row[2]
            tipo = row[3]
            freq = row[4]
            
            if t_val and msg:
                # Se for retornado como objeto time do python, formatamos para HH:MM
                if hasattr(t_val, 'strftime'):
                    time_str = t_val.strftime("%H:%M")
                else:
                    time_str = str(t_val)[:5] # Garante o formato "HH:MM"
                reminders.append({
                    "id": r_id,
                    "hora": time_str,
                    "mensagem": msg,
                    "tipo": tipo,
                    "frequencia": freq
                })
        cur.close()
    except Exception as e:
        print(f"[-] Erro ao carregar lembretes do banco de dados: {e}")
    finally:
        if conn:
            conn.close()
    return reminders

def deactivate_reminder_in_db(reminder_id):
    """Desativa um lembrete no banco de dados (para frequência única após envio)"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("""
            UPDATE p72a9cobkwj7ta3."TelegramLembretes"
            SET ativo_ = 'Não'
            WHERE id = %s;
        """, (reminder_id,))
        conn.commit()
        cur.close()
        print(f"[+] Lembrete único (id: {reminder_id}) desativado com sucesso no banco de dados.")
    except Exception as e:
        print(f"[-] Erro ao desativar lembrete (id: {reminder_id}) no banco: {e}")
    finally:
        if conn:
            conn.close()

def deve_disparar_hoje(frequencia):
    """
    Verifica se, com base na frequência cadastrada, o lembrete deve disparar hoje.
    Retorna True ou False.
    """
    if not frequencia:
        return True # Se não tem frequência, dispara todo dia (comportamento padrão)
    
    freq_norm = frequencia.strip().lower()
    
    # Se for "unico", o controle de disparo único desativa no banco após enviar
    if freq_norm == 'unico':
        return True
        
    agora = datetime.datetime.now()
    dia_semana = agora.weekday() # 0 = Segunda, 6 = Domingo
    
    if freq_norm in ['seg a sext', 'seg a sex', 'segunda a sexta', 'seg-sex']:
        return 0 <= dia_semana <= 4
        
    # Mapeamento de dias específicos em português
    dias_map = {
        'segunda': [0], 'segunda-feira': [0], 'seg': [0],
        'terça': [1], 'terca': [1], 'terça-feira': [1], 'terca-feira': [1], 'ter': [1],
        'quarta': [2], 'quarta-feira': [2], 'qua': [2],
        'quinta': [3], 'quinta-feira': [3], 'qui': [3],
        'sexta': [4], 'sexta-feira': [4], 'sex': [4],
        'sábado': [5], 'sabado': [5], 'sáb': [5], 'sab': [5],
        'domingo': [6], 'dom': [6],
        'fim de semana': [5, 6], 'fds': [5, 6]
    }
    
    if freq_norm in dias_map:
        return dia_semana in dias_map[freq_norm]
        
    # Caso o usuário digite múltiplos dias separados por vírgula, ex: "seg, qua, sex"
    partes = [p.strip() for p in freq_norm.split(',') if p.strip()]
    if partes:
        for parte in partes:
            if parte in dias_map and dia_semana in dias_map[parte]:
                return True
                
    return False

def formatar_mensagem(mensagem, tipo):
    """Formata a mensagem com base no tipo de lembrete"""
    if not tipo:
        return f"🔔 *Lembrete:* {mensagem}"
        
    tipo_norm = tipo.strip().lower()
    if tipo_norm in ['lembrete', 'lembrate']:
        prefixo = "🔔 *Lembrete:*"
    elif tipo_norm == 'compromisso':
        prefixo = "📅 *Compromisso:*"
    elif tipo_norm == 'rotina':
        prefixo = "🔄 *Rotina:*"
    else:
        prefixo = f"💡 *{tipo.capitalize()}:*"
        
    return f"{prefixo} {mensagem}"

# --- PERSISTÊNCIA DE ESTADO (chat_id, last_update_id) ---
def load_state():
    """Carrega o estado salvo do agente"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[-] Erro ao carregar arquivo de estado: {e}")
    return {"chat_id": None, "last_update_id": 0, "lembretes_enviados_hoje": []}

def save_state(state):
    """Salva o estado atual do agente"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[-] Erro ao salvar arquivo de estado: {e}")

# --- OPERAÇÕES DO TELEGRAM ---
def send_telegram_message(token, chat_id, text):
    """Envia uma mensagem de texto via Telegram API"""
    if not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"[-] Erro ao enviar mensagem para {chat_id}: {e}")
        return False

# --- LOG DE ANOTAÇÕES DIÁRIAS ---
def registrar_nota_diaria(texto):
    """Registra o texto no arquivo do dia corrente em formato Markdown"""
    os.makedirs(BASE_DIR, exist_ok=True)
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    filepath = os.path.join(BASE_DIR, f"telegram-{hoje}.md")
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    
    ja_existe = os.path.exists(filepath)
    
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            if not ja_existe:
                f.write(f"# Notas e Lembretes de {hoje}\n\n")
            f.write(f"- [{agora}] {texto}\n")
        print(f"[+] Nota registrada com sucesso em: {filepath}")
        return True
    except Exception as e:
        print(f"[-] Erro ao registrar nota diária: {e}")
        return False

# --- THREAD DE LEMBRETES AUTOMÁTICOS ---
def worker_lembretes(token):
    """Thread em background que monitora o relógio e dispara lembretes agendados"""
    print("[*] Thread de Lembretes iniciada com sucesso.")
    
    while True:
        state = load_state()
        chat_id = state.get("chat_id")
        
        if not chat_id:
            # Se não temos o chat_id do usuário, aguardamos que ele envie a primeira mensagem
            time.sleep(30)
            continue
            
        agora = datetime.datetime.now()
        hora_minuto = agora.strftime("%H:%M")
        hoje = agora.strftime("%Y-%m-%d")
        
        # Reseta o cache de lembretes do dia se mudou de dia
        historico_dia = state.get("lembretes_dia_atual", "")
        if historico_dia != hoje:
            state["lembretes_dia_atual"] = hoje
            state["lembretes_enviados_hoje"] = []
            save_state(state)
            
        enviados = state.get("lembretes_enviados_hoje", [])
        
        # Busca lembretes dinamicamente do banco de dados
        lembretes_config = get_active_reminders_from_db()
        
        # Verifica se há lembretes para disparar agora
        for lembrete in lembretes_config:
            hora_lembrete = lembrete["hora"]
            r_id = lembrete["id"]
            
            # Só dispara se bater com o minuto atual
            if hora_lembrete == hora_minuto:
                # Evita enviar o mesmo lembrete várias vezes no mesmo minuto
                chave_envio = f"{r_id}_{hora_minuto}"
                if chave_envio not in enviados:
                    # Valida se deve disparar hoje com base na frequência
                    if deve_disparar_hoje(lembrete["frequencia"]):
                        mensagem_formatada = formatar_mensagem(lembrete["mensagem"], lembrete["tipo"])
                        tipo_label = lembrete["tipo"] or "Lembrete"
                        print(f"[*] Disparando {tipo_label} (id: {r_id}, hora: {hora_minuto}, freq: {lembrete['frequencia']})...")
                        
                        if send_telegram_message(token, chat_id, mensagem_formatada):
                            # Registra também na nota diária
                            registrar_nota_diaria(f"[{tipo_label} Automático das {hora_minuto}] Enviado com sucesso.")
                            enviados.append(chave_envio)
                            state["lembretes_enviados_hoje"] = enviados
                            save_state(state)
                            
                            # Se for frequência única, desativa do banco
                            if lembrete["frequencia"] and lembrete["frequencia"].strip().lower() == 'unico':
                                deactivate_reminder_in_db(r_id)
                        else:
                            print(f"[-] Falha ao enviar lembrete {r_id} das {hora_minuto}")
                            
        time.sleep(20)  # Checa a cada 20 segundos

# --- LOGICA PRINCIPAL DE POLLING ---
def rodar_polling(token):
    """Loop principal de Long Polling para ler atualizações do Telegram"""
    print("[*] Iniciando escuta de mensagens do Telegram (Long Polling)...")
    
    # Remove qualquer webhook ativo para evitar conflitos de polling (Erro 409)
    try:
        requests.post(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=10)
    except Exception as e:
        print(f"[-] Alerta ao limpar webhook: {e}")
        
    state = load_state()
    offset = state.get("last_update_id", 0)
    
    while True:
        url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=30"
        try:
            response = requests.get(url, timeout=35)
            if response.status_code != 200:
                print(f"[-] Erro na chamada da API do Telegram (Status {response.status_code}). Tentando novamente em 10s...")
                time.sleep(10)
                continue
                
            dados = response.json()
            if not dados.get("ok"):
                print("[-] Resposta da API não retornou ok. Tentando novamente em 10s...")
                time.sleep(10)
                continue
                
            updates = dados.get("result", [])
            for update in updates:
                update_id = update.get("update_id")
                offset = update_id + 1
                
                # Salva o último update_id processado
                state["last_update_id"] = offset
                save_state(state)
                
                message = update.get("message")
                if not message:
                    continue
                    
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                texto = message.get("text")
                
                # Salva ou atualiza o chat_id do usuário (garante o envio dos lembretes)
                if state.get("chat_id") != chat_id:
                    state["chat_id"] = chat_id
                    save_state(state)
                    print(f"[+] Chat ID do usuário identificado e registrado: {chat_id}")
                    
                    # Mensagem de boas-vindas na primeira conexão
                    saudacao = (
                        "👋 *Olá! Conexão estabelecida com sucesso!*\n\n"
                        "A partir de agora, tudo que você me enviar aqui será anotado automaticamente no seu arquivo diário em:\n"
                        "`hoje/telegram-YYYY-MM-DD.md`.\n\n"
                        "Também te enviarei lembretes úteis ao longo do dia! 😉"
                    )
                    send_telegram_message(token, chat_id, saudacao)
                
                # Identifica áudios, mensagens de voz ou documentos
                voice = message.get("voice")
                audio = message.get("audio")
                document = message.get("document")
                
                if voice or audio:
                    media_obj = voice if voice else audio
                    file_id = media_obj.get("file_id")
                    print(f"[*] Áudio recebido (file_id: {file_id}). Transcrevendo...")
                    
                    # Notificar o usuário que está processando
                    send_telegram_message(token, chat_id, "🎙️ _Processando e transcrevendo seu áudio..._")
                    
                    texto_transcrito = transcrever_audio(token, file_id)
                    texto_formatado = f"🎙️ (Áudio Transcrito): {texto_transcrito}"
                    
                    if registrar_nota_diaria(texto_formatado):
                        resposta = f"✅ *Transcrito e anotado!*\n\n🎙️ \"_{texto_transcrito}_\""
                        send_telegram_message(token, chat_id, resposta)
                        
                elif document:
                    file_name = document.get("file_name", "arquivo.txt")
                    texto_formatado = f"📄 (Arquivo Recebido): {file_name}"
                    if registrar_nota_diaria(texto_formatado):
                        send_telegram_message(token, chat_id, f"✅ Arquivo `{file_name}` anotado nas notas diárias!")
                
                elif texto:
                    print(f"[*] Mensagem recebida: '{texto}'")
                    # Registra a nota diária bruta
                    if registrar_nota_diaria(texto):
                        # Envia uma confirmação visual rápida
                        send_telegram_message(token, chat_id, "✅ *Anotado no arquivo diário!*")
                        
        except requests.exceptions.RequestException as re:
            print(f"[-] Erro de conexão de rede no polling: {re}. Tentando novamente em 10s...")
            time.sleep(10)
        except Exception as e:
            print(f"[-] Ocorreu um erro inesperado no polling: {e}. Tentando novamente em 10s...")
            time.sleep(10)

def main():
    if not TELEGRAM_TOKEN:
        print("[-] Erro: TELEGRAM_TOKEN não configurado no arquivo .env!")
        sys.exit(1)
        
    print("[*] Iniciando Agente de Telegram...")
    print(f"[*] Diretório de Notas Diárias: {BASE_DIR}")
    
    # Inicia a thread de lembretes automáticos
    t_lembretes = threading.Thread(target=worker_lembretes, args=(TELEGRAM_TOKEN,), daemon=True)
    t_lembretes.start()
    
    # Inicia o polling na thread principal
    try:
        rodar_polling(TELEGRAM_TOKEN)
    except KeyboardInterrupt:
        print("\n[*] Encerrando o agente graciosamente por interrupção do usuário. Até logo!")
        sys.exit(0)

if __name__ == '__main__':
    main()
