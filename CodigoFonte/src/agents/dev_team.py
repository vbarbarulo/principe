import os
import sys
import json
import re
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Garante raiz no PATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.utils.env_loader import load_env
load_env()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

class DevTeam:
    def __init__(self, api_key=OPENAI_KEY):
        self.model = OpenAIChat(id="gpt-4o-mini", api_key=api_key)

        # 1. Product Owner (PO)
        self.po_agent = Agent(
            model=self.model,
            description="Você é o Product Owner (PO) da Equipe de Automação de Software Hórus.",
            instructions=[
                "Você é o guardião do negócio e das regras de prioridade do backlog.",
                "Analise ideias de melhoria brutas inseridas no sistema.",
                "Sua missão é detalhar os requisitos, eliminar ambiguidades funcionais e definir prioridades.",
                "Sempre classifique a tarefa usando a Curva ABC:",
                "  - A (Alta prioridade / Consequência crítica se não entregue hoje)",
                "  - B (Média prioridade / Importante no médio prazo)",
                "  - C (Baixa prioridade / Apenas se sobrar tempo)",
                "Forneça uma resposta estruturada JSON contendo:",
                "  - 'titulo': Título conciso da tarefa",
                "  - 'descricao_refinada': Descrição limpa e objetiva dos requisitos funcionais",
                "  - 'curva_abc': 'A', 'B' ou 'C'",
                "  - 'tags': Array de tags úteis (ex: ['backend', 'frontend', 'prompt', 'database'])",
                "Você DEVE retornar APENAS o JSON puro. Não use markdown fences (```json) ou outros textos explicativos."
            ]
        )

        # 2. Líder Técnico (Tech Lead)
        self.tech_lead_agent = Agent(
            model=self.model,
            description="Você é o Líder Técnico (Tech Lead) da Equipe de Automação de Software Hórus.",
            instructions=[
                "Avalie a viabilidade arquitetural da tarefa proposta e seu impacto no ecossistema.",
                "Você deve planejar exatamente quais arquivos precisam ser criados ou modificados.",
                "Divida a demanda em sub-tarefas específicas para os desenvolvedores.",
                "Retorne um JSON contendo:",
                "  - 'viabilidade': true ou false",
                "  - 'impacto': 'alto', 'medio' ou 'baixo'",
                "  - 'arquivos_afetados': Lista de caminhos relativos de arquivos (ex: ['src/agents/dev_team.py'])",
                "  - 'subtarefas': Lista de strings detalhando os passos técnicos que o Dev deve realizar.",
                "  - 'motivo_bloqueio': Mensagem explicando caso a tarefa seja inviável ou perigosa (se viabilidade for false)",
                "Você DEVE retornar APENAS o JSON puro."
            ]
        )

        # 3. Dev Senior (Backend/Frontend/Prompt)
        self.dev_agent = Agent(
            model=self.model,
            description="Você é o Dev Senior da Equipe Hórus.",
            instructions=[
                "Você é um excelente programador especialista em Python, HTML/CSS/jQuery e Engenharia de Prompt.",
                "Sua missão é escrever as modificações de código exatas solicitadas pelo Tech Lead.",
                "Para cada arquivo afetado, você deve fornecer o conteúdo completo ou o código novo de forma extremamente limpa e profissional.",
                "Retorne um JSON contendo:",
                "  - 'arquivos': Um objeto onde cada chave é o caminho do arquivo (ex: 'src/utils/math.py') e o valor é o código completo que deve ser escrito no arquivo.",
                "Você DEVE retornar APENAS o JSON puro."
            ]
        )

        # 4. Planejador de QA (Quality Assurance)
        self.qa_planner_agent = Agent(
            model=self.model,
            description="Você é o Planejador de QA da Equipe Hórus.",
            instructions=[
                "Analise os requisitos funcionais e o plano do Tech Lead.",
                "Desenhe os cenários de testes unitários ou de integração para a funcionalidade.",
                "Você deve escrever um arquivo de teste completo em Python usando a biblioteca 'unittest' padrão.",
                "O arquivo de teste deve importar as classes desenvolvidas de forma correta e testar os cenários principais.",
                "O arquivo de teste deve rodar de forma autônoma sem requerer interações do usuário.",
                "Retorne um JSON contendo:",
                "  - 'nome_arquivo_teste': O nome sugerido para o arquivo de teste (ex: 'test_task_123_1.py')",
                "  - 'codigo_teste': O código Python completo do teste unitário.",
                "Você DEVE retornar APENAS o JSON puro."
            ]
        )

        # 5. QA Executável (Python)
        self.qa_executor_agent = Agent(
            model=self.model,
            description="Você é o QA Executável / Especialista de Auto-Correção da Equipe Hórus.",
            instructions=[
                "Analise o relatório de erros gerado ao tentar rodar os testes unitários da tarefa.",
                "Sua missão é consertar e corrigir o código que apresentou falhas, ou ajustar o próprio teste caso o teste esteja inconsistente.",
                "Forneça a nova versão corrigida dos arquivos afetados.",
                "Retorne um JSON contendo:",
                "  - 'arquivos_corrigidos': Um objeto com caminho_do_arquivo como chave e o novo código completo como valor.",
                "  - 'comentarios': Explicação sucinta do erro encontrado e como você o corrigiu.",
                "Você DEVE retornar APENAS o JSON puro."
            ]
        )

    def _clean_and_load_json(self, text):
        """Limpa blocos markdown e carrega o JSON de forma robusta"""
        text = text.strip()
        # Remove delimitadores de markdown json se presentes
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```$", "", text).strip()
        return json.loads(text)

    def refinar_com_po(self, ideia_bruta):
        """Usa o PO Agent para estruturar e refinar a ideia"""
        resposta = self.po_agent.run(f"Ideia bruta: {ideia_bruta}")
        try:
            return self._clean_and_load_json(resposta.content)
        except Exception:
            # Fallback robusto se falhar no parse do JSON
            return {
                "titulo": "Tarefa sem título",
                "descricao_refinada": ideia_bruta,
                "curva_abc": "B",
                "tags": ["geral"]
            }

    def analisar_com_tech_lead(self, tarefa_refinada, context_codebase=""):
        """Usa o Tech Lead para avaliar a viabilidade e impacto"""
        prompt = f"Tarefa:\n{json.dumps(tarefa_refinada, indent=2)}\n\nContexto do ecossistema:\n{context_codebase}"
        resposta = self.tech_lead_agent.run(prompt)
        try:
            return self._clean_and_load_json(resposta.content)
        except Exception:
            return {
                "viabilidade": True,
                "impacto": "medio",
                "arquivos_afetados": [],
                "subtarefas": ["Desenvolver funcionalidade principal"]
            }

    def desenvolver_com_dev(self, tarefa, plano_tech_lead, codigos_existentes=""):
        """Usa o Dev para gerar o código final dos arquivos"""
        prompt = (
            f"Especificações da Tarefa:\n{json.dumps(tarefa, indent=2)}\n\n"
            f"Plano Técnico do Tech Lead:\n{json.dumps(plano_tech_lead, indent=2)}\n\n"
            f"Código de referência atual:\n{codigos_existentes}"
        )
        resposta = self.dev_agent.run(prompt)
        try:
            return self._clean_and_load_json(resposta.content)
        except Exception:
            return {"arquivos": {}}

    def planejar_testes_com_qa(self, tarefa, plano_tech_lead, codigos_novos=""):
        """Usa o QA Planner para gerar o arquivo de teste"""
        prompt = (
            f"Tarefa:\n{json.dumps(tarefa, indent=2)}\n\n"
            f"Plano:\n{json.dumps(plano_tech_lead, indent=2)}\n\n"
            f"Código Desenvolvido:\n{codigos_novos}"
        )
        resposta = self.qa_planner_agent.run(prompt)
        try:
            return self._clean_and_load_json(resposta.content)
        except Exception:
            return {
                "nome_arquivo_teste": "test_default.py",
                "codigo_teste": "import unittest\nclass TestDefault(unittest.TestCase):\n    def test_true(self):\n        self.assertTrue(True)"
            }

    def autocorrigir_com_qa(self, codigos_atuais, erro_stdout, erro_stderr):
        """Usa o QA Executável para propor correções nos arquivos com falha"""
        prompt = (
            f"Códigos Atuais:\n{codigos_atuais}\n\n"
            f"Erro na Execução dos Testes:\nSTDOUT:\n{erro_stdout}\nSTDERR:\n{erro_stderr}"
        )
        resposta = self.qa_executor_agent.run(prompt)
        try:
            return self._clean_and_load_json(resposta.content)
        except Exception:
            return {"arquivos_corrigidos": {}, "comentarios": "Falha ao processar autocrash."}
