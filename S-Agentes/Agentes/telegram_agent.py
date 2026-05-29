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
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_DIR = '/mnt/c/principe/0 -NotasRapidas'
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_agent_state.json')

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
    reminders = {}
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
        # Seleciona apenas os ativos
        cur.execute("""
            SELECT hora_, mensagem_ 
            FROM p72a9cobkwj7ta3."TelegramLembretes" 
            WHERE ativo_ IS NULL OR ativo_ IN ('Sim', 'true', '1');
        """)
        rows = cur.fetchall()
        for row in rows:
            t_val = row[0]
            msg = row[1]
            if t_val and msg:
                # Se for retornado como objeto time do python, formatamos para HH:MM
                if hasattr(t_val, 'strftime'):
                    time_str = t_val.strftime("%H:%M")
                else:
                    time_str = str(t_val)[:5] # Garante o formato "HH:MM"
                reminders[time_str] = msg
        cur.close()
    except Exception as e:
        print(f"[-] Erro ao carregar lembretes do banco de dados: {e}")
    finally:
        if conn:
            conn.close()
    return reminders

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
        
        # Verifica se há lembrete para disparar agora
        if hora_minuto in lembretes_config and hora_minuto not in enviados:
            mensagem = lembretes_config[hora_minuto]
            print(f"[*] Disparando lembrete agendado ({hora_minuto})...")
            
            if send_telegram_message(token, chat_id, mensagem):
                # Registra também na nota diária
                registrar_nota_diaria(f"[Lembrete Automático das {hora_minuto}] Enviado com sucesso.")
                enviados.append(hora_minuto)
                state["lembretes_enviados_hoje"] = enviados
                save_state(state)
            else:
                print(f"[-] Falha ao enviar lembrete das {hora_minuto}")
                
        time.sleep(20)  # Checa a cada 20 segundos

# --- LOGICA PRINCIPAL DE POLLING ---
def rodar_polling(token):
    """Loop principal de Long Polling para ler atualizações do Telegram"""
    print("[*] Iniciando escuta de mensagens do Telegram (Long Polling)...")
    
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
                        "`0 -NotasRapidas/telegram-YYYY-MM-DD.md`.\n\n"
                        "Também te enviarei lembretes úteis ao longo do dia! 😉"
                    )
                    send_telegram_message(token, chat_id, saudacao)
                
                # Identifica áudios ou mensagens de voz
                voice = message.get("voice")
                audio = message.get("audio")
                
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
                
                elif texto:
                    print(f"[*] Mensagem recebida: '{texto}'")
                    # Registra a nota
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
