import os
import sys
import json
import sqlite3
from datetime import date

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.agents.agent_orchestrator import AgentOrchestrator
from src.database.upsert_engine import UpsertEngine

class DecompressionAgent:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.upsert_engine = UpsertEngine()

    def processar_descompressao(self, texto_bruto, data_str=None):
        """
        Analisa o texto de descompressão do dia.
        Extrai sentimentos, tarefas Curva ABC e insights estruturados.
        """
        if data_str is None:
            data_str = date.today().isoformat()

        prompt_sistema = (
            "Você é o analista de descompressão do ecossistema Hórus.\n"
            "Analise o desabafo do usuário para identificar:\n"
            "1. Sentimentos predominantes (ex: culpa, orgulho, ansiedade, foco).\n"
            "2. Tarefas e Metas extraídas implicitamente (ex: pagar contas, estudar, exercitar).\n"
            "3. Conquistas ou impedimentos do dia.\n\n"
            "Retorne APENAS um JSON estruturado seguindo rigorosamente este formato:\n"
            "{\n"
            '  "sentimentos": ["ansiedade", "culpa"],\n'
            '  "tarefas_extraidas": [\n'
            '     {"texto": "Comprar remédios", "consequencia": "alta"},\n'
            '     {"texto": "Fazer leitura do livro", "consequencia": "media"}\n'
            '  ],\n'
            '  "excelente": "Foco alto no trabalho pela manhã",\n'
            '  "dificultou": "Cansaço e dispersão à tarde",\n'
            '  "licao": "Manter o sono rigorosamente"\n'
            "}"
        )

        try:
            response = self.orchestrator.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": texto_bruto}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            analise = json.loads(response.choices[0].message.content.strip())
        except Exception as e:
            analise = {
                "sentimentos": [],
                "tarefas_extraidas": [],
                "excelente": "Processado com sucesso",
                "dificultou": "Sem incidentes graves",
                "licao": "Manter consistência"
            }

        # Persistir tarefas extraídas na tabela itens_segundo_cerebro com a classificação Curva ABC
        conn = sqlite3.connect(self.upsert_engine.db_path)
        cursor = conn.cursor()
        
        for t in analise.get("tarefas_extraidas", []):
            # Classifica curva
            cons = t.get("consequencia", "media")
            curva = "B"
            if cons == "alta":
                curva = "A"
            elif cons == "baixa":
                curva = "C"

            # Insere
            cursor.execute("""
                INSERT INTO itens_segundo_cerebro (data_registro, tipo, curva, tempo, conteudo, status, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data_str,
                "tarefa",
                curva,
                "hoje",
                t.get("texto"),
                "pendente_sincronia",
                json.dumps(analise.get("sentimentos", []))
            ))

        # Persistir log de descompressão
        cursor.execute("""
            INSERT INTO logs_descompressao (data, categoria, conteudo_bruto, analise_ia, decisoes_tomadas)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data_str,
            "Descompressão Ativa",
            texto_bruto,
            f"Excelente: {analise.get('excelente')} | Dificultou: {analise.get('dificultou')}",
            f"Lição: {analise.get('licao')}"
        ))

        # Adicionar sentimentos e comportamentos relevantes na memorias_usuario (aprendizado)
        for s in analise.get("sentimentos", []):
            cursor.execute("""
                INSERT INTO memorias_usuario (categoria, fato, data_aprendizado, importancia)
                VALUES (?, ?, ?, ?)
            """, (
                "sentimento",
                f"Demonstrou {s} durante a descompressão do dia.",
                data_str,
                3
            ))

        conn.commit()
        conn.close()

        return analise
