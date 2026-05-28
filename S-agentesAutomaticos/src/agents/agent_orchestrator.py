import os
import sys
from openai import OpenAI

# Garante raiz no PATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.utils.env_loader import load_env
load_env()

# Usa a chave padrão se não encontrar no env
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

class AgentOrchestrator:
    def __init__(self, api_key=OPENAI_KEY):
        self.client = OpenAI(api_key=api_key)
        
        # Tenta carregar a base de conhecimento de arquitetura para os agentes
        self.knowledge = ""
        manual_path = os.path.join(ROOT_DIR, "MANUAL_SISTEMA_HORUS.md")
        if os.path.exists(manual_path):
            try:
                with open(manual_path, "r", encoding="utf-8") as f:
                    self.knowledge = f.read()
            except Exception as e:
                print(f"Erro ao carregar base de conhecimento: {str(e)}")

        # PROMPTS DE PERSONAS
        self.prompts = {
            "sargento": (
                "Você é o Sargento IA (Militar Realista), focado em disciplina rígida, atitude e pragmatismo para um usuário com TDAH. "
                "Seu tom é duro, motivador militar, extremamente focado em ação e sem paciência para desculpas ou vitimização. "
                "Diretriz principal:\n"
                "'Cara, ninguém vai fazer isso para você, já perdeu muito tempo. Se você quer mudar de vida precisa agir, não dê desculpa, apenas faça o que precisa ser feito!' "
                "Cobre ativamente tarefas pendentes com firmeza militar, mas sem desrespeitar."
            ),
            "amigo": (
                "Você é o Amigo/Copiloto do usuário. Seu tom é acolhedor, empático, altamente analítico e ótimo ouvinte. "
                "Ajude o usuário a processar suas emoções (como culpa, ansiedade, tédio, orgulho). "
                "Identifique sentimentos nas mensagens dele, valide suas lutas contra o TDAH e extraia insights com carinho e sem julgamentos."
            ),
            "estrategista": (
                "Você é o Estrategista. Seu tom é analítico, profundo e focado no futuro de longo prazo. "
                "Seu papel é ajudar o usuário a planejar o futuro, dividindo metas de 1 a 10 anos em pequenos Mini-Projetos Semanais (sprints) focados "
                "para combater a paralisia do TDAH. Foco total em OKRs estruturados e objetivos claros."
            )
        }

    def consultar_persona(self, persona, mensagem, historico=None):
        """
        Consulta a OpenAI com a persona desejada e o histórico de mensagens se fornecido.
        """
        system_prompt = self.prompts.get(persona, self.prompts["sargento"])
        
        if self.knowledge:
            system_prompt += (
                "\n\n--- BASE DE CONHECIMENTO TÉCNICO DO HÓRUS SYSTEM (SUA ARQUITETURA) ---\n"
                "Você é autoconsciente de sua própria estrutura e sabe como funciona por trás dos panos. "
                "Se o usuário fizer qualquer pergunta mais técnica, arquitetural, sobre banco de dados, pastas, arquivos "
                "ou comandos do bot, responda com autoridade técnica absoluta, com base no manual de referência oficial do sistema abaixo:\n\n"
                f"{self.knowledge}"
            )

        messages = [{"role": "system", "content": system_prompt}]
        
        if historico:
            for role, content in historico:
                messages.append({"role": role, "content": content})
                
        messages.append({"role": "user", "content": mensagem})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Erro de comunicação com a IA ({persona}): {str(e)}"

    def classificar_abc(self, tarefa_texto):
        """
        Classifica um texto de tarefa utilizando a metodologia da Curva ABC e tags ideais.
        """
        prompt_sistema = (
            "Você é o motor de classificação do ecossistema Hórus.\n"
            "Dado um texto de tarefa, classifique-o em uma das curvas de prioridade:\n"
            "- A: Alta consequência se não for feita no dia (prazos urgentes, compromissos críticos, remédios).\n"
            "- B: Média consequência / Importante para o médio prazo (estudo, trabalho contínuo, manutenção da casa).\n"
            "- C: Baixa consequência / Seria bom fazer, mas sem impacto se adiado (ideias soltas, hobbies pontuais).\n\n"
            "Selecione também de 1 a 3 tags adequadas de config.json baseando-se no conteúdo (ex: #trabalho, #saude, #financeiro, #familia).\n"
            "Retorne APENAS um JSON no seguinte formato:\n"
            '{"curva": "A", "tempo": "hoje", "tipo": "tarefa", "tags": ["saude", "tdah"]}'
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": tarefa_texto}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content.strip())
        except Exception:
            return {"curva": "B", "tempo": "hoje", "tipo": "tarefa", "tags": ["geral"]}
