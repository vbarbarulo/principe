#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente Organizador de Tarefas - Hórus System
Lê um bloco de texto contendo tarefas diárias, interpreta o contexto (ex: Prioridades),
e insere de forma estruturada no banco de dados PostgreSQL.
"""

import os
import sys
import re
from datetime import date
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
DB_HOST = os.getenv('DB_HOST', '89.116.214.181')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'nocodb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'i8PvK1TUvfmKhYasSMLE')

def parse_texto_tarefas(texto):
    """
    Interpreta o texto livre e extrai as tarefas estruturadas.
    """
    linhas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
    tarefas = []
    contexto_atual = "Geral"
    prioridade_atual = "Média"
    
    for linha in linhas:
        # Se for um cabeçalho / contexto
        if linha.lower().startswith("prioridades") or "prioridade" in linha.lower():
            contexto_atual = "Prioridades"
            prioridade_atual = "Alta"
            continue
        elif ":" in linha and not linha.startswith(("-", "*", "•")):
            contexto_atual = linha.replace(":", "").strip()
            prioridade_atual = "Média"
            continue
            
        # Verifica se é um item da lista
        match = re.match(r'^[-*•\d\.\s]+(.*)', linha)
        if match:
            tarefa_texto = match.group(1).strip()
            if tarefa_texto:
                tarefas.append({
                    'tarefa': tarefa_texto,
                    'prioridade': prioridade_atual,
                    'contexto': contexto_atual
                })
        else:
            # Se for linha comum sem marcador, assume como tarefa se não for vazia
            tarefas.append({
                'tarefa': linha,
                'prioridade': prioridade_atual,
                'contexto': contexto_atual
            })
            
    return tarefas

def salvar_tarefas_no_banco(tarefas):
    """
    Insere as tarefas extraídas diretamente no banco de dados na tabela 'Tarefas'.
    """
    if not tarefas:
        print("[-] Nenhuma tarefa encontrada para salvar.")
        return False
        
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
        
        # SQL para inserção na tabela de Entrada 'Tarefas'
        sql = """
            INSERT INTO p72a9cobkwj7ta3."Tarefas" 
            ("Tarefa", "Status", "Prioridade", "DT_inicio", "ano", "M_s", "tipo_tarefa", "Projetos", "execu__o_") 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        hoje = date.today()
        ano = str(hoje.year)
        mes = str(hoje.month).zfill(2)
        data_inicio = holidays = hoje.strftime('%Y-%m-%d')
        
        inseridas = 0
        for t in tarefas:
            cur.execute(sql, (
                t['tarefa'],
                'Em Aberto',
                'p4',
                data_inicio,
                ano,
                mes,
                'TAREFA',
                '📦 Caixa de Entrada',
                '00 - Nova Tarefa'
            ))
            inseridas += 1
            
        conn.commit()
        print(f"[+] {inseridas} tarefas salvas com sucesso na tabela de Organização do Dia!")
        cur.close()
        return True
    except Exception as e:
        print(f"[-] Erro ao salvar tarefas no PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 agente_organizador.py \"<texto com as tarefas>\"")
        sys.exit(1)
        
    texto_entrada = sys.argv[1]
    
    # Se o argumento for um caminho de arquivo existente, lê o arquivo
    if os.path.exists(texto_entrada):
        with open(texto_entrada, 'r', encoding='utf-8') as f:
            texto_entrada = f.read()
            
    print("[*] Processando texto de entrada...")
    tarefas = parse_texto_tarefas(texto_entrada)
    
    print(f"[+] Tarefas identificadas ({len(tarefas)}):")
    for i, t in enumerate(tarefas, 1):
        print(f"  {i}. {t['tarefa']}")
        
    salvar_tarefas_no_banco(tarefas)

if __name__ == '__main__':
    main()
