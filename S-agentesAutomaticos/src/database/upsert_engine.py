import os
import sys
import sqlite3
import json
from datetime import datetime

# Garante que o diretório raiz esteja no PATH para imports do Python
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.utils.rotinas_parser import RotinasParser

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "agent.db")

class UpsertEngine:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.parser = RotinasParser()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def upsert_rotina(self, rotina_id, data_str, acoes_concluidas=None, acoes_puladas=None, dados_capturados=None, horarios_reais=None, observacoes=None):
        """
        Realiza o Upsert Inteligente na tabela registros_rotina utilizando a chave composta hash (data-rotina_id).
        """
        record_id = f"{data_str}-{rotina_id}"
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Carrega registro existente se houver
        cursor.execute("SELECT acoes_concluidas, acoes_puladas, dados_capturados, horarios_reais, observacoes FROM registros_rotina WHERE id = ?", (record_id,))
        row = cursor.fetchone()

        db_concluidas = []
        db_puladas = []
        db_capturados = {}
        db_horarios = {}
        db_observacoes = ""

        if row:
            db_concluidas = json.loads(row[0]) if row[0] else []
            db_puladas = json.loads(row[1]) if row[1] else []
            db_capturados = json.loads(row[2]) if row[2] else {}
            db_horarios = json.loads(row[3]) if row[3] else {}
            db_observacoes = row[4] if row[4] else ""

        # 2. Mescla os novos dados (Intelligent Merge)
        if acoes_concluidas:
            # Union of lists to avoid duplicates
            db_concluidas = list(set(db_concluidas + acoes_concluidas))
            # Remove completed tasks from skipped list if they were marked as completed now
            db_puladas = [x for x in db_puladas if x not in acoes_concluidas]
        
        if acoes_puladas:
            db_puladas = list(set(db_puladas + acoes_puladas))
            db_concluidas = [x for x in db_concluidas if x not in acoes_puladas]

        if dados_capturados:
            db_capturados.update(dados_capturados)

        if horarios_reais:
            db_horarios.update(horarios_reais)

        if observacoes:
            if db_observacoes:
                if observacoes not in db_observacoes:
                    db_observacoes += " | " + observacoes
            else:
                db_observacoes = observacoes

        # 3. Calcula o status dinâmico
        # Busca definição de rotinas estáticas para ver quantas tarefas o bloco possui
        rotinas_def = self.parser.parse()
        status = "incompleto"
        if rotina_id in rotinas_def:
            total_tarefas = len(rotinas_def[rotina_id]["tarefas"])
            # Considera também sub-tarefas se houver
            sub_total = 0
            for t in rotinas_def[rotina_id]["tarefas"]:
                sub_total += len(t.get("subtarefas", []))
            
            total_itens = total_tarefas + sub_total
            concluidos_total = len(db_concluidas)

            if total_itens > 0:
                percent = (concluidos_total / total_itens) * 100
                if percent >= 100:
                    status = "completo"
                elif percent > 0:
                    status = "parcial"

        # 4. Grava/Insere no SQLite
        cursor.execute("""
        INSERT INTO registros_rotina (id, rotina_id, data, acoes_concluidas, acoes_puladas, dados_capturados, horarios_reais, observacoes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            acoes_concluidas=excluded.acoes_concluidas,
            acoes_puladas=excluded.acoes_puladas,
            dados_capturados=excluded.dados_capturados,
            horarios_reais=excluded.horarios_reais,
            observacoes=excluded.observacoes,
            status=excluded.status
        """, (
            record_id,
            rotina_id,
            data_str,
            json.dumps(db_concluidas),
            json.dumps(db_puladas),
            json.dumps(db_capturados),
            json.dumps(db_horarios),
            db_observacoes,
            status
        ))

        conn.commit()
        conn.close()
        return record_id, status

if __name__ == "__main__":
    engine = UpsertEngine()
    # Teste rápido
    from datetime import date
    today = date.today().isoformat()
    record, stat = engine.upsert_rotina(
        rotina_id="acordar",
        data_str=today,
        acoes_concluidas=["acordar_01", "acordar_03"],
        dados_capturados={"peso_kg": 82.5},
        horarios_reais={"acordar_01": "06:05"}
    )
    print(f"Upsert de teste bem sucedido: ID={record}, Status={stat}")
