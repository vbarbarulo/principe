import os
import sys
import json
import sqlite3
import datetime
import subprocess

# Garante raiz no PATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.agents.dev_team import DevTeam
from src.utils.git_utils import GitUtils

DB_PATH = os.path.join(ROOT_DIR, "data", "agent.db")
REPORTS_DIR = os.path.join(ROOT_DIR, "exports", "diarios")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TESTS_DIR, exist_ok=True)

class KanbanPipeline:
    def __init__(self, api_key=None):
        self.dev_team = DevTeam(api_key=api_key) if api_key else DevTeam()
        self.git = GitUtils(repo_path=ROOT_DIR)

    def _get_db_connection(self):
        return sqlite3.connect(DB_PATH)

    def create_task(self, ideia_bruta):
        """Passo 1: PO analisa a ideia e cria a task no banco (estado 'refining')"""
        # Refina a ideia com o PO
        refinada = self.dev_team.refinar_com_po(ideia_bruta)
        
        # Gera ID Único
        task_id = f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        branch_name = f"task-{task_id}"
        
        # Salva no banco de dados
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO kanban_tasks 
            (id, titulo, descricao_original, requisitos_refinados, status, branch_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            refinada.get("titulo", "Tarefa sem Título"),
            ideia_bruta,
            refinada.get("descricao_refinada", ""),
            "refining",
            branch_name
        ))
        conn.commit()
        conn.close()
        
        refinada["id"] = task_id
        refinada["branch_name"] = branch_name
        return refinada

    def planejar_e_aprovar(self, task_id):
        """Passo 2: Tech Lead avalia viabilidade e gera subtarefas (estado 'developing')"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, requisitos_refinados FROM kanban_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"error": f"Tarefa {task_id} não encontrada."}
        
        titulo, requisitos_refinados = row
        tarefa = {
            "id": task_id,
            "titulo": titulo,
            "descricao_refinada": requisitos_refinados
        }

        # Lê contexto simples do projeto para passar ao Tech Lead (ex: lista de arquivos do diretório src)
        arquivos_projeto = []
        for root, dirs, files in os.walk(os.path.join(ROOT_DIR, "src")):
            for f in files:
                if f.endswith(".py"):
                    arquivos_projeto.append(os.path.relpath(os.path.join(root, f), ROOT_DIR))
        
        context_codebase = f"Arquivos Python no projeto:\n" + "\n".join(arquivos_projeto)

        # Análise do Tech Lead
        plano = self.dev_team.analisar_com_tech_lead(tarefa, context_codebase)

        if not plano.get("viabilidade", True):
            # Tarefa bloqueada
            cursor.execute("UPDATE kanban_tasks SET status = ?, subtarefas_json = ? WHERE id = ?", 
                           ("blocked", json.dumps(plano.get("subtarefas", [])), task_id))
            conn.commit()
            conn.close()
            return {
                "status": "blocked",
                "motivo": plano.get("motivo_bloqueio", "Bloqueado pelo Tech Lead"),
                "plano": plano
            }

        # Atualiza banco com subtarefas e prossegue para desenvolvimento
        cursor.execute("UPDATE kanban_tasks SET status = ?, subtarefas_json = ? WHERE id = ?",
                       ("developing", json.dumps(plano.get("subtarefas", [])), task_id))
        conn.commit()
        conn.close()

        return {
            "status": "developing",
            "plano": plano
        }

    def executar_desenvolvimento_e_qa(self, task_id, plano_tech_lead):
        """Passo 3: Criar branch Git, Dev codifica, QA testa, auto-corrige e finaliza com merge"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, requisitos_refinados, branch_name FROM kanban_tasks WHERE id = ?", (task_id,))
        titulo, requisitos_refinados, branch_name = cursor.fetchone()
        
        tarefa = {
            "id": task_id,
            "titulo": titulo,
            "descricao_refinada": requisitos_refinados
        }

        # 1. Controle de versão: Cria e muda para a branch da task
        print(f"[{task_id}] Criando branch {branch_name}...")
        self.git.create_and_checkout_branch(branch_name)

        # 2. Ler conteúdo dos arquivos afetados para fornecer como contexto ao Dev
        arquivos_afetados = plano_tech_lead.get("arquivos_afetados", [])
        codigos_existentes = ""
        for arq in arquivos_afetados:
            caminho_full = os.path.join(ROOT_DIR, arq)
            if os.path.exists(caminho_full):
                try:
                    with open(caminho_full, "r", encoding="utf-8") as f:
                        codigos_existentes += f"\n--- Arquivo: {arq} ---\n{f.read()}\n"
                except Exception:
                    pass

        # 3. Desenvolvedor cria/modifica os arquivos
        print(f"[{task_id}] Dev programando...")
        dev_res = self.dev_team.desenvolver_com_dev(tarefa, plano_tech_lead, codigos_existentes)
        arquivos_gerados = dev_res.get("arquivos", {})

        # Escreve os arquivos gerados no disco local
        for arq, conteudo in arquivos_gerados.items():
            caminho_full = os.path.join(ROOT_DIR, arq)
            os.makedirs(os.path.dirname(caminho_full), exist_ok=True)
            with open(caminho_full, "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"[{task_id}] Arquivo gravado/atualizado: {arq}")

        # 4. QA Planner desenha os testes
        print(f"[{task_id}] QA desenhando cenários de teste...")
        qa_res = self.dev_team.planejar_testes_com_qa(tarefa, plano_tech_lead, json.dumps(arquivos_gerados, indent=2))
        nome_teste = qa_res.get("nome_arquivo_teste", f"test_{task_id}_1.py")
        codigo_teste = qa_res.get("codigo_teste", "")

        caminho_teste = os.path.join(TESTS_DIR, nome_teste)
        with open(caminho_teste, "w", encoding="utf-8") as f:
            f.write(codigo_teste)
        print(f"[{task_id}] Arquivo de teste gravado: tests/{nome_teste}")

        # 5. Execução dos testes e auto-correção recursiva
        print(f"[{task_id}] Rodando testes automatizados...")
        limite_retries = 3
        test_passed = False
        exec_output = ""
        exec_error = ""

        cursor.execute("UPDATE kanban_tasks SET status = ? WHERE id = ?", ("testing", task_id))
        conn.commit()

        for tentativa in range(1, limite_retries + 1):
            # Executa o teste usando python3 no WSL
            cmd = ["python3", "-m", "unittest", f"tests/{nome_teste}"]
            result = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
            
            exec_output = result.stdout
            exec_error = result.stderr
            test_passed = result.returncode == 0

            print(f"[{task_id}] Tentativa {tentativa} de teste: {'PASSOU' if test_passed else 'FALHOU'}")
            
            if test_passed:
                break
            
            # Se falhou, aciona o QA Executável para auto-correção
            print(f"[{task_id}] Auto-correção acionada para tentativa {tentativa}...")
            codigos_atuais_str = ""
            for arq in arquivos_gerados.keys():
                caminho_full = os.path.join(ROOT_DIR, arq)
                if os.path.exists(caminho_full):
                    with open(caminho_full, "r", encoding="utf-8") as f:
                        codigos_atuais_str += f"\n--- {arq} ---\n{f.read()}\n"

            correcoes = self.dev_team.autocorrigir_com_qa(codigos_atuais_str, exec_output, exec_error)
            arquivos_corrigidos = correcoes.get("arquivos_corrigidos", {})
            
            if not arquivos_corrigidos:
                print(f"[{task_id}] QA não conseguiu propor correções automáticas.")
                break
                
            for arq, conteudo in arquivos_corrigidos.items():
                caminho_full = os.path.join(ROOT_DIR, arq)
                with open(caminho_full, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                # Atualiza no cache local de gerados
                arquivos_gerados[arq] = conteudo
                print(f"[{task_id}] Arquivo auto-corrigido gravado: {arq}")

        # 6. Geração de Relatório de Entrega / Fechamento de Card
        status_final = "done" if test_passed else "blocked"
        resultado_teste_str = "SUCESSO" if test_passed else "FALHA APÓS AUTO-CORREÇÃO"
        
        relatorio_markdown = f"""# 📝 Relatório Técnico de Entrega - {task_id}

## 📋 Resumo da Demanda
*   **Título:** {titulo}
*   **ID da Task:** `{task_id}`
*   **Data de Conclusão:** {datetime.date.today().strftime('%d/%m/%Y')}
*   **Status de QA:** **{resultado_teste_str}**

## 💻 Arquivos Modificados/Criados
{chr(10).join([f'*   `{arq}`' for arq in arquivos_gerados.keys()])}
*   `tests/{nome_teste}` (Arquivo de Teste)

## 🧪 Parecer do Processo de QA
*   **Comando Executado:** `python3 -m unittest tests/{nome_teste}`
*   **Resultado de Saída:**
```text
{exec_output or exec_error}
```

## 🛠️ Intervenções e Auto-Correções Realizadas
{"Nenhuma auto-correção foi necessária." if not test_passed and tentativa == 1 else f"Foram realizadas tentativas de auto-correção pelo agente executor. Testes finalizados com {resultado_teste_str}."}
"""
        
        # Salva o relatório no diretório 'diarios'
        caminho_relatorio = os.path.join(REPORTS_DIR, f"relatorio_{task_id}.md")
        with open(caminho_relatorio, "w", encoding="utf-8") as f:
            f.write(relatorio_markdown)
        print(f"[{task_id}] Relatório gravado em: exports/diarios/relatorio_{task_id}.md")

        # Commita os novos arquivos na branch do git
        self.git.add_all_and_commit(f"feat: entrega de codigo para {task_id}")

        # 7. Mesclar branch de volta à master
        if test_passed:
            print(f"[{task_id}] Mesclando branch {branch_name} com a master...")
            self.git.merge_branch(branch_name, target_branch="master")
            print(f"[{task_id}] Mesclagem concluída!")
        else:
            # Se deu ruim, volta para a master sem mesclar e deixa a branch isolada
            self.git.checkout_branch("master")
            print(f"[{task_id}] Testes falharam. Branch {branch_name} mantida intacta para depuração manual.")

        # Atualiza estado final no banco de dados
        cursor.execute("""
            UPDATE kanban_tasks 
            SET status = ?, relatorio_qa = ? 
            WHERE id = ?
        """, (status_final, relatorio_markdown, task_id))
        conn.commit()
        conn.close()

        return {
            "status": status_final,
            "relatorio_path": f"exports/diarios/relatorio_{task_id}.md",
            "test_passed": test_passed,
            "relatorio": relatorio_markdown
        }
