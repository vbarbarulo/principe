import os
import sys
import glob
from openai import OpenAI

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.utils.env_loader import load_env
load_env()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

class MemoryRAG:
    def __init__(self, key=OPENAI_KEY, reports_dir=None):
        self.client = OpenAI(api_key=key)
        if reports_dir is None:
            self.reports_dir = os.path.join(ROOT_DIR, "diarios")
        else:
            self.reports_dir = reports_dir

    def buscar_memoria(self, pergunta):
        """
        Varre todos os diários locais em Markdown e utiliza o LLM para responder 
        a pergunta subjetiva do usuário correlacionando os sentimentos históricos.
        """
        arquivos = glob.glob(os.path.join(self.reports_dir, "relatorio_*.md"))
        if not arquivos:
            return "Ainda não encontrei nenhum diário local para pesquisar suas memórias."

        # Lê os últimos 7 diários para evitar estourar tokens e obter maior relevância temporal
        arquivos.sort(reverse=True)
        contexto_diarios = []
        
        for arq in arquivos[:7]:
            base = os.path.basename(arq)
            data = base.replace("relatorio_", "").replace(".md", "")
            try:
                with open(arq, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Remove frontmatter para economizar tokens
                    if "---" in content:
                        parts = content.split("---")
                        if len(parts) >= 3:
                            content = "---".join(parts[2:])
                contexto_diarios.append(f"📅 Data: {data}\n{content[:800]}")
            except Exception:
                pass

        contexto_completo = "\n\n===\n\n".join(contexto_diarios)

        prompt_sistema = (
            "Você é a Memória Semântica do ecossistema Hórus.\n"
            "Sua tarefa é analisar o histórico de diários fornecidos abaixo e responder à pergunta do usuário.\n"
            "Seja extremamente acolhedor, empático e factual. Cite as datas correspondentes aos fatos citados.\n\n"
            f"--- HISTÓRICO DE DIÁRIOS ---\n{contexto_completo}"
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": pergunta}
                ],
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Erro ao acessar memórias: {str(e)}"

if __name__ == "__main__":
    rag = MemoryRAG()
    res = rag.buscar_memoria("Como foi meu sentimento essa semana?")
    print(res)
