#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Tasks Migrator - Hórus System
Agente focado em migrar os dados locais da tabela "Tarefas" (Caixa de Entrada) para a tabela consolidada "FuturoGestão" no PostgreSQL.
"""

import os
import sys
import argparse
from datetime import date
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
DB_HOST = os.getenv('DB_HOST', '89.116.214.181')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'nocodb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'i8PvK1TUvfmKhYasSMLE')

def migrar_tarefas():
    """Migra dados da tabela 'Tarefas' para a tabela 'FuturoGestão' aplicando transformações e de-para"""
    print("[*] Iniciando a migração da Caixa de Entrada para a Gestão de Prioridades...")
    
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        # Usamos DictCursor para podermos acessar os campos pelos nomes das colunas físicos da origem
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # 1. Busca todos os registros da tabela de origem 'Tarefas'
        print("[*] Buscando registros na tabela de origem 'Tarefas'...")
        cur.execute('SELECT * FROM p72a9cobkwj7ta3."Tarefas";')
        rows = cur.fetchall()
        print(f"[+] Total de registros encontrados para migração: {len(rows)}")
        
        if not rows:
            print("[*] Nenhum registro encontrado para migrar.")
            cur.close()
            return True
            
        # Dicionário de registros mapeados indexados por ID
        results = {}
        ids_para_deletar = []
        
        for row in rows:
            row_id = row['id']
            if not row_id:
                continue
                
            ids_para_deletar.append(str(row_id))
            
            # --- ROTINA DE DATA DE CONCLUSÃO ---
            dt_finalizado = row['DT_finalizado']
            status_lower = str(row['Status'] or '').strip().lower()
            
            if status_lower in ['ok', 'concluído', 'concluida', 'feito', 'finalizado']:
                if not dt_finalizado:
                    dt_finalizado = date.today().strftime('%Y-%m-%d')
                else:
                    # Converte objeto date para string YYYY-MM-DD
                    dt_finalizado = str(dt_finalizado)[:10]
            else:
                dt_finalizado = str(dt_finalizado)[:10] if dt_finalizado else None

            # --- ROTINA DE CRONOGRAMA ANOMES ---
            ano = str(row['ano'] or '2026').strip()
            mes = str(row['M_s'] or '').strip()
            if not mes:
                mes = '01'
            else:
                # Preenche com zero à esquerda se for número simples de 1 dígito (ex: '5' -> '05')
                mes = mes.zfill(2)
            cronograma_ano_mes = f"{ano}-{mes}"

            # --- DE-PARA DE TIPO DE TAREFA ---
            tipo_origem = row['tipo_de_tarefa_'] or row['tipo_tarefa']
            tipo_de_tarefa = 'TAREFA'
            if tipo_origem:
                tipo_origem_upper = str(tipo_origem).strip().upper()
                if 'PROJETO' in tipo_origem_upper:
                    tipo_de_tarefa = 'PROJETO'
                elif 'SUB' in tipo_origem_upper:
                    tipo_de_tarefa = 'SUB PROJETO'
                elif 'OKR' in tipo_origem_upper:
                    tipo_de_tarefa = 'OKR'
                elif 'KR' in tipo_origem_upper:
                    tipo_de_tarefa = 'KR'
            
            # --- MAPEAMENTO COMPLETO ---
            mapped_data = {
                'id_original': str(row_id),
                'okr': row['Okr'] or '',
                'kr': row['KR'] or '',
                'projects': row['Projetos'] or '📦 Caixa de Entrada',
                'sub_projects': row['SubProjetos'] or '',
                'tasks': row['Tarefa'] or '',
                'link': '',
                'assignee': 'Vinicius',
                'date': str(row['DT_inicio'])[:10] if row['DT_inicio'] else None,
                'status': row['Status'] or 'Em Aberto',
                'tipo_de_tarefa': tipo_de_tarefa,
                'fase_detalhada': row['fase_detalhada'] or '',
                'horas': row['horas'] or '',
                'cronograma_ano_mes': cronograma_ano_mes,
                'data_conclusao': dt_finalizado,
                'esta_okr': 'Não',
                'esta_gestao_prioridades': 'Não',
                'departamento': row['Departamento'] or '',
                'estimativa': row['Nivel_de_dificuldade'] or '',
                'prioridade': row['Prioridade'] or '',
                'empresa': 'Futuro'
            }
            
            results[row_id] = mapped_data
            
        # 2. Executa a deleção segmentada para evitar qualquer duplicidade
        if ids_para_deletar:
            print("[*] Executando deleção segmentada dos registros anteriores no destino...")
            # Divide em lotes de 500 para segurança de consulta SQL
            for i in range(0, len(ids_para_deletar), 500):
                lote = ids_para_deletar[i:i+500]
                cur.execute('DELETE FROM p72a9cobkwj7ta3."FuturoGestão" WHERE "Tarefa" IN %s;', (tuple(lote),))
                cur.execute('DELETE FROM p72a9cobkwj7ta3."FuturoGestao_Complementar" WHERE id_tarefa IN %s;', (tuple(lote),))
                
        # 3. Gravação em lote na tabela consolidada "FuturoGestão"
        print("[*] Gravando registros migrados no PostgreSQL...")
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
        
        for row_id, data in results.items():
            try:
                cur.execute(sql, (
                    data['id_original'],
                    data['okr'],
                    data['kr'],
                    data['projects'],
                    data['sub_projects'],
                    data['tasks'],
                    data['link'],
                    data['assignee'],
                    data['date'],
                    data['status'],
                    data['tipo_de_tarefa'],
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
                
                cur.execute(sql_comp, (data['id_original'],))
                inserted += 1
            except Exception as ex:
                print(f"[-] Erro ao gravar registro {row_id}: {ex}")
                errors += 1
                
        conn.commit()
        print(f"[+] Migração concluída com absoluto sucesso!")
        print(f"[+] Registros inseridos no consolidado: {inserted}, Erros: {errors}")
        cur.close()
        return True
    except Exception as e:
        print(f"[-] Erro grave na conexão ou banco de dados durante a migração: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="Database Tasks Migrator - Hórus System")
    parser.add_argument('--sincronizar', '-s', action='store_true', help="Atalho para executar a migração e sincronização.")
    args = parser.parse_args()
    
    # Se não passar nenhum argumento, assume a sincronização automática
    migrar_tarefas()

if __name__ == '__main__':
    main()
