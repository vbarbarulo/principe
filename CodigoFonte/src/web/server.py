import os
import sys
import json
import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

# Garante o diretório do banco correto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.utils.env_loader import load_env
load_env()

DB_PATH = os.path.join(BASE_DIR, "data", "agent.db")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

os.makedirs(STATIC_DIR, exist_ok=True)

def db_migration():
    """Garante que a coluna de prioridade exista na tabela de tarefas do Kanban."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(kanban_tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        if "prioridade" not in columns:
            cursor.execute("ALTER TABLE kanban_tasks ADD COLUMN prioridade INTEGER DEFAULT 0")
            conn.commit()
            print("🗄️ Coluna 'prioridade' adicionada com sucesso à tabela kanban_tasks.")
        conn.close()
    except Exception as e:
        print(f"Erro ao rodar migração de prioridade no SQLite: {e}")

class HorusHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Evita poluir o console com logs de requisição comuns
        pass

    def get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # API Endpoints
        if path == "/api/tasks":
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, titulo, descricao_original, requisitos_refinados, subtarefas_json, branch_name, status, relatorio_qa, prioridade FROM kanban_tasks ORDER BY prioridade ASC, id DESC")
                tasks = []
                for row in cursor.fetchall():
                    tasks.append(dict(row))
                conn.close()
                self.send_json(tasks)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        elif path == "/api/health":
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, data, hora_dormiu, hora_acordou, nota_sono, peso, relato_sono, relato_acordar FROM checkin_saude ORDER BY data DESC LIMIT 15")
                health_logs = []
                for row in cursor.fetchall():
                    health_logs.append(dict(row))
                conn.close()
                self.send_json(health_logs)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        # Servir Arquivos Estáticos
        if path == "/" or path == "/index.html":
            file_path = os.path.join(STATIC_DIR, "index.html")
            mime_type = "text/html"
        else:
            filename = path.lstrip("/")
            file_path = os.path.join(STATIC_DIR, filename)
            if filename.endswith(".css"):
                mime_type = "text/css"
            elif filename.endswith(".js"):
                mime_type = "application/javascript"
            elif filename.endswith(".png"):
                mime_type = "image/png"
            elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                mime_type = "image/jpeg"
            elif filename.endswith(".ico"):
                mime_type = "image/x-icon"
            else:
                mime_type = "text/plain"

        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro ao ler arquivo: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/tasks":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)

                import datetime
                # Gerar ID único se não enviado
                task_id = data.get("id") or f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                titulo = data.get("titulo", "Nova Tarefa")
                desc = data.get("descricao_original", "Criada via Painel Web")
                status = data.get("status", "backlog")
                branch = data.get("branch_name") or f"task-{task_id}"

                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO kanban_tasks (id, titulo, descricao_original, status, branch_name, prioridade)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (task_id, titulo, desc, status, branch))
                conn.commit()
                conn.close()

                self.send_json({"success": True, "id": task_id})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        elif path == "/api/tasks/reorder":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)

                ordered_ids = data.get("ids", [])
                if not ordered_ids:
                    self.send_json({"error": "Lista de IDs é necessária"}, 400)
                    return

                conn = self.get_db_connection()
                cursor = conn.cursor()
                for idx, task_id in enumerate(ordered_ids):
                    cursor.execute("UPDATE kanban_tasks SET prioridade = ? WHERE id = ?", (idx, task_id))
                conn.commit()
                conn.close()

                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        elif path == "/api/chat-po":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)

                task_id = data.get("id")
                user_msg = data.get("message")
                history = data.get("history", []) # list of {"role": "...", "content": "..."}

                if not task_id or not user_msg:
                    self.send_json({"error": "ID da tarefa e mensagem são obrigatórios"}, 400)
                    return

                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT titulo, descricao_original, requisitos_refinados, status FROM kanban_tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                conn.close()

                if not row:
                    self.send_json({"error": "Tarefa não encontrada"}, 404)
                    return

                task_title = row["titulo"]
                task_desc = row["descricao_original"]
                task_reqs = row["requisitos_refinados"] or "Nenhum requisito refinado ainda."

                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY", "")
                client = OpenAI(api_key=api_key)

                po_prompt = (
                    "Você é o Product Owner (PO) do Hórus System. Sua missão é atuar como ponte entre a visão de negócios do usuário e a implementação técnica.\n"
                    "Estamos refinando o seguinte card do backlog:\n"
                    f"- Título: {task_title}\n"
                    f"- Descrição Original: {task_desc}\n"
                    f"- Requisitos Refinados Atuais: {task_reqs}\n\n"
                    "Diretrizes:\n"
                    "1. Explore a necessidade do usuário fazendo perguntas se houver dúvidas, ou melhore e detalhe os requisitos.\n"
                    "2. Defina os Critérios de Aceitação de forma clara em formato Markdown.\n"
                    "3. Classifique a tarefa na Curva ABC (A, B ou C) e decida quando ela está madura e robusta o suficiente para avançar para a fase de Desenvolvimento (status 'developing').\n"
                    "4. Se você considerar que a especificação e refinamento estão maduros, robustos e prontos para desenvolvimento, defina o campo 'ready_to_advance' como true.\n\n"
                    "Você DEVE responder exclusivamente com um objeto JSON no seguinte formato (sem caracteres de markdown adicionais, sem ```json, apenas o JSON puro):\n"
                    "{\n"
                    "  \"reply\": \"Texto da sua resposta direcionada ao usuário explicando suas dúvidas, conclusões ou sugestões...\",\n"
                    "  \"refined_requirements\": \"Especificação técnica completa dos requisitos refinados e critérios de aceitação em formato markdown (com checkboxes para os critérios de aceitação)...\",\n"
                    "  \"ready_to_advance\": true ou false\n"
                    "}"
                )

                messages = [{"role": "system", "content": po_prompt}]
                for h_msg in history:
                    messages.append({"role": h_msg["role"], "content": h_msg["content"]})
                
                messages.append({"role": "user", "content": user_msg})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7
                )

                response_text = response.choices[0].message.content.strip()
                try:
                    clean_text = response_text
                    if clean_text.startswith("```"):
                        clean_text = clean_text.split("\n", 1)[1]
                    if clean_text.endswith("```"):
                        clean_text = clean_text.rsplit("\n", 1)[0]
                    clean_text = clean_text.strip()
                    
                    po_response = json.loads(clean_text)
                except Exception as parse_err:
                    print(f"Erro ao parsear resposta da IA: {parse_err}. Resposta bruta: {response_text}")
                    po_response = {
                        "reply": response_text,
                        "refined_requirements": task_reqs,
                        "ready_to_advance": False
                    }

                # Salva os requisitos refinados e o status no banco de dados
                conn = self.get_db_connection()
                cursor = conn.cursor()
                if po_response.get("ready_to_advance"):
                    cursor.execute("""
                        UPDATE kanban_tasks 
                        SET status = 'developing', requisitos_refinados = ? 
                        WHERE id = ?
                    """, (po_response.get("refined_requirements"), task_id))
                else:
                    cursor.execute("""
                        UPDATE kanban_tasks 
                        SET status = 'refining', requisitos_refinados = ? 
                        WHERE id = ? AND status = 'backlog'
                    """, (po_response.get("refined_requirements"), task_id))
                    cursor.execute("""
                        UPDATE kanban_tasks 
                        SET requisitos_refinados = ? 
                        WHERE id = ?
                    """, (po_response.get("refined_requirements"), task_id))
                conn.commit()
                conn.close()

                self.send_json(po_response)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()

    def do_PUT(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/tasks":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)

                task_id = data.get("id")
                if not task_id:
                    self.send_json({"error": "ID da tarefa obrigatório"}, 400)
                    return

                titulo = data.get("titulo")
                desc = data.get("descricao_original")
                reqs = data.get("requisitos_refinados")
                subtasks = data.get("subtarefas_json")
                branch = data.get("branch_name")
                status = data.get("status")
                relatorio = data.get("relatorio_qa")

                conn = self.get_db_connection()
                cursor = conn.cursor()

                update_fields = []
                params = []
                for field, val in [
                    ("titulo", titulo),
                    ("descricao_original", desc),
                    ("requisitos_refinados", reqs),
                    ("subtarefas_json", subtasks),
                    ("branch_name", branch),
                    ("status", status),
                    ("relatorio_qa", relatorio)
                ]:
                    if val is not None:
                        update_fields.append(f"{field} = ?")
                        params.append(val)

                if not update_fields:
                    self.send_json({"error": "Nenhum campo para atualizar informado"}, 400)
                    conn.close()
                    return

                params.append(task_id)
                query = f"UPDATE kanban_tasks SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, tuple(params))
                conn.commit()
                conn.close()

                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/tasks":
            try:
                query_params = urllib.parse.parse_qs(parsed_url.query)
                task_id = query_params.get("id", [None])[0]
                if not task_id:
                    self.send_json({"error": "ID da tarefa é obrigatório para deletar"}, 400)
                    return

                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM kanban_tasks WHERE id = ?", (task_id,))
                conn.commit()
                conn.close()

                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()

def run_server(port=5050):
    db_migration()
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, HorusHTTPRequestHandler)
    print(f"🌍 Servidor Web Hórus rodando localmente na porta {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

def start_web_server_thread(port=5050):
    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    run_server()
