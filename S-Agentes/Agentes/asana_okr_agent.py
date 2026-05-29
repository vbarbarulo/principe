#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Asana OKR Agent - Hórus System
Agente focado exclusivamente em baixar dados de OKRs do Asana e sincronizar com o PostgreSQL (NocoDB).
"""

import os
import sys
import json
import argparse
import requests
import psycopg2
from psycopg2 import extras

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
ASANA_TOKEN = os.getenv('ASANA_TOKEN')
PROJECT_OKR = os.getenv('ASANA_PROJECT_OKR', '1212434383653814')

DB_HOST = os.getenv('DB_HOST', '89.116.214.181')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'nocodb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'i8PvK1TUvfmKhYasSMLE')

# Pasta temporária para arquivos locais
TEMP_DIR = '/mnt/c/principe/Z-ArquivosProcessados/TempAssana'
OKR_FILE_NAME = 'okr_tasks.json'
OKR_CACHE_NAME = 'okr_tasks_cache.json'

# --- FUNÇÕES DE AUXÍLIO ---
def get_headers():
    return {
        'Authorization': f'Bearer {ASANA_TOKEN}',
        'Accept': 'application/json',
        'User-Agent': 'AsanaOkrAgentPython/1.0'
    }

def call_asana(url):
    """Wrapper para chamadas à API do Asana"""
    try:
        response = requests.get(url, headers=get_headers(), timeout=60)
        if response.status_code == 200:
            return response.json()
        print(f"[-] Erro na chamada Asana ({url}): Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[-] Exceção na chamada Asana: {e}")
    return None

def get_custom_field_value(task, field_name):
    """Extrai o valor de um campo customizado do Asana pelo nome"""
    custom_fields = task.get('custom_fields', [])
    for cf in custom_fields:
        if cf.get('name') == field_name:
            if cf.get('enum_value'):
                return cf['enum_value'].get('name')
            return cf.get('display_value') or cf.get('text_value') or cf.get('number_value')
    return None

def expandir_subtasks_recursivo(task, level=1):
    """Busca e expande as subtasks de uma tarefa recursivamente até o nível desejado"""
    if level >= 5:
        return
    
    task_id = task.get('gid')
    num_subtasks = task.get('num_subtasks', 0)
    
    if num_subtasks > 0 or task.get('subtasks'):
        print(f"[*] Baixando subtasks para a tarefa: {task.get('name')} (Nível {level})")
        fields = "name,notes,completed,completed_at,due_on,assignee,assignee.name,permalink_url,subtasks,num_subtasks,custom_fields,projects"
        url = f"https://app.asana.com/api/1.0/tasks/{task_id}/subtasks?opt_expand={fields}"
        dados_subtasks = call_asana(url)
        
        if dados_subtasks and 'data' in dados_subtasks:
            subtasks = dados_subtasks['data']
            task['subtasks'] = subtasks
            for subtask in subtasks:
                expandir_subtasks_recursivo(subtask, level + 1)

# --- AÇÃO: BAIXAR DADOS ---
def baixar_dados():
    """Baixa os JSONs brutos do projeto de OKRs e salva na pasta TempAssana"""
    print("[*] Iniciando download dos dados de OKR do Asana...")
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    if not ASANA_TOKEN:
        print("[-] Erro: ASANA_TOKEN não configurado no ambiente/.env")
        return False

    # Campos a expandir no projeto raiz
    fields = "name,notes,completed,completed_at,due_on,assignee,assignee.name,permalink_url,subtasks,num_subtasks,custom_fields,parent,parent.name,parent.parent,parent.parent.name,parent.parent.parent,parent.parent.parent.name,projects"
    url = f'https://app.asana.com/api/1.0/projects/{PROJECT_OKR}/tasks?opt_expand={fields}'
    
    # Se já existir um arquivo atual, rotacionamos ele como cache/anterior para sabermos o que deletar depois
    filepath = os.path.join(TEMP_DIR, OKR_FILE_NAME)
    cachepath = os.path.join(TEMP_DIR, OKR_CACHE_NAME)
    if os.path.exists(filepath):
        if os.path.exists(cachepath):
            os.remove(cachepath)
        os.rename(filepath, cachepath)
        print("[+] Arquivo anterior movido para o cache de exclusão segmentada.")

    print(f"[*] Buscando tarefas do projeto OKR: {url}")
    dados = call_asana(url)
    if dados and 'data' in dados:
        # Expande as subtasks de cada tarefa raiz recursivamente
        print("[*] Expandindo subtasks recursivamente de todas as tarefas raiz...")
        for task in dados['data']:
            expandir_subtasks_recursivo(task, level=1)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        print(f"[+] Salvo com sucesso em: {filepath}")
        return True
    else:
        print("[-] Falha ao baixar dados de OKR.")
        # Restaura o arquivo do cache se o download falhou
        if os.path.exists(cachepath):
            os.rename(cachepath, filepath)
        return False

# --- AÇÃO: PROCESSAR E SINCRONIZAR ---
def extract_hierarchy_from_parent(task):
    """Retorna (okr, kr, project, sub_project) subindo a árvore de parent no Asana"""
    chain = []
    curr = task.get('parent')
    while curr:
        chain.append(curr)
        curr = curr.get('parent')
        
    okr = ''
    kr = ''
    project = ''
    sub_project = ''
    
    chain.reverse()
    
    for parent_obj in chain:
        name = parent_obj.get('name', '')
        if not name:
            continue
        name_upper = name.upper()
        if 'OKR' in name_upper:
            okr = name
        elif 'KR' in name_upper:
            kr = name
        else:
            if not project:
                project = name
            elif not sub_project:
                sub_project = name
                
    return okr, kr, project, sub_project

def process_task_tree(task, context, level, results):
    """Processa a árvore de tarefas recursivamente estruturando a hierarquia"""
    task_id = task.get('gid')
    if not task_id:
        return
        
    name = task.get('name', '')
    if not name or not name.strip():
        return

    current_context = context.copy()
    num_subtasks = task.get('num_subtasks', 0)
    
    p_okr, p_kr, p_proj, p_sub_proj = extract_hierarchy_from_parent(task)
    if p_okr and (not current_context.get('okr') or 'OKR' not in current_context.get('okr', '').upper()):
        current_context['okr'] = p_okr
    if p_kr and (not current_context.get('kr') or 'KR' not in current_context.get('kr', '').upper()):
        current_context['kr'] = p_kr
    
    tipo = 'TAREFA'
    if level == 1:
        tipo = 'OKR'
        current_context['okr'] = name
    elif level == 2:
        tipo = 'KR'
        current_context['kr'] = name
    elif level == 3:
        if num_subtasks == 0:
            tipo = 'TAREFA'
            current_context['projects'] = '📦 Ações Diretas do KR'
            current_context['sub_projects'] = 'Tarefas Soltas'
            current_context['tasks'] = name
        else:
            tipo = 'PROJETO'
            current_context['projects'] = name
    elif level == 4:
        if num_subtasks == 0:
            tipo = 'TAREFA'
            current_context['sub_projects'] = '📦 Tarefas do Projeto'
            current_context['tasks'] = name
        else:
            tipo = 'SUB PROJETO'
            current_context['sub_projects'] = name
    else:
        tipo = 'TAREFA'
        current_context['tasks'] = name

    fase_detalhada = get_custom_field_value(task, 'Fase') or get_custom_field_value(task, 'FaseDetalhada')
    cronograma = get_custom_field_value(task, 'Cronograma') or get_custom_field_value(task, 'CronogramaAnoMes')
    tipo_card = get_custom_field_value(task, 'TipoCard')
    horas = get_custom_field_value(task, 'horas')
    
    # Novos campos customizados solicitados pelo usuário
    prioridade_val = get_custom_field_value(task, 'Prioridade') or get_custom_field_value(task, 'Priority') or get_custom_field_value(task, 'prioridade')
    estimativa_val = get_custom_field_value(task, 'Estimativa') or get_custom_field_value(task, 'Size') or get_custom_field_value(task, 'estimativa') or get_custom_field_value(task, 'size')
    departamento_val = get_custom_field_value(task, 'Departamento') or get_custom_field_value(task, 'Area') or get_custom_field_value(task, 'Área') or get_custom_field_value(task, 'departamento')

    card_status = 'Concluído' if task.get('completed', False) else 'Em Aberto'
    
    completed_at = task.get('completed_at')
    if completed_at:
        completed_at = completed_at[:10]  # Extrai YYYY-MM-DD

    # Determina a presença em projetos com base no contexto herdado ou nos projetos diretos do Asana
    esta_okr_flag = current_context.get('esta_okr_flag', False)
    esta_priori_flag = current_context.get('esta_priori_flag', False)
    
    task_projects = task.get('projects', [])
    if task_projects:
        for proj in task_projects:
            proj_name_upper = proj.get('name', '').upper()
            proj_id = proj.get('gid')
            if 'OKR' in proj_name_upper or proj_id == PROJECT_OKR:
                esta_okr_flag = True
            if 'PRIORIDADE' in proj_name_upper or 'INOVAÇÃO' in proj_name_upper or proj_id == '1212946699570594':
                esta_priori_flag = True
                
    current_context['esta_okr_flag'] = esta_okr_flag
    current_context['esta_priori_flag'] = esta_priori_flag

    mapped_data = {
        'id_asana': task_id,
        'okr': current_context.get('okr', ''),
        'kr': current_context.get('kr', ''),
        'projects': current_context.get('projects', ''),
        'sub_projects': current_context.get('sub_projects', ''),
        'tasks': current_context.get('tasks', ''),
        'link': task.get('permalink_url', ''),
        'assignee': task.get('assignee', {}).get('name', 'Não atribuído') if task.get('assignee') else 'Não atribuído',
        'date': task.get('due_on'),
        'status': card_status,
        'tipo_de_tarefa': tipo,
        'fase_detalhada': fase_detalhada or '',
        'cronograma_ano_mes': cronograma or '',
        'tipo_card': tipo_card or '',
        'horas': horas or '',
        'data_conclusao': completed_at,
        'esta_okr': 'Sim' if esta_okr_flag else 'Não',
        'esta_gestao_prioridades': 'Sim' if esta_priori_flag else 'Não',
        'prioridade': prioridade_val or '',
        'estimativa': estimativa_val or '',
        'departamento': departamento_val or '',
        'empresa': 'Futuro'
    }

    if task_id not in results:
        results[task_id] = mapped_data
    else:
        existing = results[task_id]
        if not existing['okr'] and mapped_data['okr']:
            existing['okr'] = mapped_data['okr']
        if not existing['kr'] and mapped_data['kr']:
            existing['kr'] = mapped_data['kr']

    if level < 5:
        subtasks = task.get('subtasks', [])
        for st in subtasks:
            process_task_tree(st, current_context, level + 1, results)

def sincronizar_banco():
    """Lê os arquivos de OKR baixados, desduplica e popula o PostgreSQL"""
    print("[*] Iniciando leitura dos arquivos de OKR e sincronização...")
    
    okr_file = os.path.join(TEMP_DIR, OKR_FILE_NAME)
    cache_file = os.path.join(TEMP_DIR, OKR_CACHE_NAME)
    
    if not os.path.exists(okr_file):
        print("[-] Erro: Arquivo local de OKR não encontrado. Execute '--action baixar' primeiro.")
        return False
        
    results = {}
    
    print("[*] Processando tarefas do OKR...")
    with open(okr_file, 'r', encoding='utf-8') as f:
        okr_data = json.load(f)
        for root_task in okr_data.get('data', []):
            process_task_tree(root_task, {}, 1, results)
                
    # Coleta IDs antigos para exclusão segmentada inteligente
    ids_para_deletar = set()
    
    # 1. IDs do cache anterior (se houver)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                old_results = {}
                for root_task in old_data.get('data', []):
                    process_task_tree(root_task, {}, 1, old_results)
                ids_para_deletar.update(old_results.keys())
        except Exception as e:
            print(f"[-] Erro ao ler cache anterior: {e}")
            
    # 2. Garante que os IDs novos também sejam limpos antes de reinserir (evita duplicidade)
    ids_para_deletar.update(results.keys())
    
    print(f"[+] Total de cards únicos de OKR processados: {len(results)}")
    print(f"[+] IDs selecionados para limpeza segmentada no banco: {len(ids_para_deletar)}")
    
    print("[*] Conectando ao banco de dados PostgreSQL...")
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
        
        # Limpeza seletiva: remove apenas as tarefas que este agente gerencia
        if ids_para_deletar:
            print("[*] Executando deleção segmentada dos registros anteriores de OKR...")
            # Divide em lotes de 500 para evitar limites de parâmetros na consulta SQL
            ids_list = list(ids_para_deletar)
            for i in range(0, len(ids_list), 500):
                lote = ids_list[i:i+500]
                cur.execute('DELETE FROM p72a9cobkwj7ta3."FuturoGestão" WHERE "Tarefa" IN %s;', (tuple(lote),))
                cur.execute('DELETE FROM p72a9cobkwj7ta3."FuturoGestao_Complementar" WHERE id_tarefa IN %s;', (tuple(lote),))
        
        # Insere os dados mapeados
        print("[*] Gravando novos dados de OKR no PostgreSQL...")
        sql = """
            INSERT INTO p72a9cobkwj7ta3."FuturoGestão" 
            ("Tarefa", "ORK", "RK", "PROJETOS", "SUB_PROJETTOS_", "TAREFAS", "Link_do_Card", "Responsavel", "Data", "Status_do_card", "tipo_de_tarefa", "Fase_Detalhada", "horas", "CronogramaAnoMes", "data_conclusao", "esta_okr", "esta_gestao_prioridades", "Departamento", "estimativa", "prioridade", "Empresa") 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        sql_comp = """
            INSERT INTO p72a9cobkwj7ta3."FuturoGestao_Complementar" (id_tarefa) 
            VALUES (%s) ON CONFLICT (id_tarefa) DO NOTHING
        """
        
        inserted = 0
        errors = 0
        
        for idx, (asana_id, data) in enumerate(results.items()):
            try:
                due_date = data['date'] if data['date'] else None
                
                cur.execute(sql, (
                    str(asana_id),
                    data['okr'],
                    data['kr'],
                    data['projects'],
                    data['sub_projects'],
                    data['tasks'],
                    data['link'],
                    data['assignee'],
                    due_date,
                    data['status'],
                    data['tipo_card'],
                    data['fase_detalhada'],
                    data['horas'],
                    data['cronograma_ano_mes'],
                    data['data_conclusao'],
                    data['esta_okr'],
                    data['esta_gestao_prioridades'],
                    data['departamento'],
                    data['estimativa'],
                    data['prioridade'],
                    data['empresa']
                ))
                
                cur.execute(sql_comp, (str(asana_id),))
                inserted += 1
            except Exception as ex:
                print(f"[-] Erro ao gravar card {asana_id}: {ex}")
                errors += 1
                
        conn.commit()
        print(f"[+] Sincronização de OKR concluída: {inserted} registros inseridos, {errors} erros.")
        cur.close()
        return True
    except Exception as e:
        print(f"[-] Erro de conexão/banco de dados: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- MÉTODOS CLI ---
def main():
    parser = argparse.ArgumentParser(description="Asana OKR Agent - Hórus System")
    parser.add_argument('--action', choices=['baixar', 'sincronizar', 'completo'], required=False,
                        help="Ação a ser executada: baixar, sincronizar ou completo.")
    parser.add_argument('--baixar', '-b', action='store_true', help="Atalho para baixar dados do Asana.")
    parser.add_argument('--sincronizar', '-s', action='store_true', help="Atalho para sincronizar com o banco.")
    parser.add_argument('--completo', '-c', action='store_true', help="Atalho para baixar e sincronizar.")
    
    args = parser.parse_args()
    
    action = args.action
    if args.baixar:
        action = 'baixar'
    elif args.sincronizar:
        action = 'sincronizar'
    elif args.completo:
        action = 'completo'
        
    if not action:
        parser.print_help()
        sys.exit(1)
    
    if action == 'baixar':
        success = baixar_dados()
        sys.exit(0 if success else 1)
    elif action == 'sincronizar':
        success = sincronizar_banco()
        sys.exit(0 if success else 1)
    elif action == 'completo':
        success_download = baixar_dados()
        if not success_download:
            print("[-] Cancelando sincronização devido a falha no download.")
            sys.exit(1)
        success_sync = sincronizar_banco()
        sys.exit(0 if success_sync else 1)

if __name__ == '__main__':
    main()
