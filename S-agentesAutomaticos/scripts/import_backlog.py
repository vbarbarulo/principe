import os
import sys
import re
import sqlite3

# Garante raiz no PATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

DB_PATH = os.path.join(ROOT_DIR, "data", "agent.db")

# Caminhos prováveis para o arquivo de temas e tasks
caminhos_arquivo = [
    os.path.join(ROOT_DIR, "..", "Analise do meu sistema", "3-temas_e_tasks.md"),
    os.path.join(ROOT_DIR, "..", "Analise do meu sistema", "3-temas_e_tasks.md"),
    "/mnt/c/Users/vinic/OneDrive/Área de Trabalho/Analise do meu sistema/3-temas_e_tasks.md",
    "c:\\Users\\vinic\\OneDrive\\Área de Trabalho\\Analise do meu sistema\\3-temas_e_tasks.md"
]

def localizar_arquivo():
    for caminho in caminhos_arquivo:
        if os.path.exists(caminho):
            print(f"Arquivo encontrado em: {caminho}")
            return caminho
    return None

def parse_markdown(caminho_md):
    with open(caminho_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Vamos dividir o arquivo por seções de Task "### T"
    pattern = r"###\s*(T\d+\.\d+):\s*(.*?)\n(.*?)(?=\n###\s*T|\n##\s*|$)"
    matches = re.findall(pattern, content, re.DOTALL)

    tasks = []
    for task_id, titulo, corpo in matches:
        task_id = task_id.strip()
        titulo = titulo.strip()
        corpo = corpo.strip()

        # Extrai descrição
        desc_match = re.search(r"\*\s*\*\*Descrição:\*\*\s*(.*?)(?=\n\*|$)", corpo, re.DOTALL)
        descricao = desc_match.group(1).strip() if desc_match else corpo

        # Extrai critérios de aceitação
        criterios = ""
        criterios_match = re.search(r"\*\s*\*\*Critérios de Aceite:\*\*\s*(.*)", corpo, re.DOTALL)
        if criterios_match:
            criterios = criterios_match.group(1).strip()

        tasks.append({
            "id": task_id,
            "titulo": f"[{task_id}] {titulo}",
            "descricao_original": f"Descrição:\n{descricao}\n\nCritérios de Aceite:\n{criterios}",
            "requisitos_refinados": f"Importado do Backlog 3-temas_e_tasks.md.\n\nDescrição:\n{descricao}\n\nCritérios de Aceite:\n{criterios}",
            "subtarefas_json": "[]",
            "branch_name": f"task-{task_id.lower().replace('.', '_')}",
            "status": "backlog"
        })
    
    return tasks

def importar_para_db(tasks):
    if not os.path.exists(DB_PATH):
        print(f"Erro: Banco de dados não encontrado em {DB_PATH}. Inicialize-o primeiro.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inseridos = 0
    atualizados = 0

    for task in tasks:
        # Verifica se já existe a task com o mesmo ID
        cursor.execute("SELECT id FROM kanban_tasks WHERE id = ?", (task["id"],))
        exists = cursor.fetchone()

        if exists:
            # Atualiza mantendo o status original caso já tenha sido movida na esteira
            cursor.execute("""
                UPDATE kanban_tasks 
                SET titulo = ?, descricao_original = ?, requisitos_refinados = ?, branch_name = ?
                WHERE id = ?
            """, (task["titulo"], task["descricao_original"], task["requisitos_refinados"], task["branch_name"], task["id"]))
            atualizados += 1
        else:
            # Insere como backlog
            cursor.execute("""
                INSERT INTO kanban_tasks 
                (id, titulo, descricao_original, requisitos_refinados, subtarefas_json, branch_name, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task["id"], task["titulo"], task["descricao_original"], task["requisitos_refinados"], task["subtarefas_json"], task["branch_name"], task["status"]))
            inseridos += 1

    conn.commit()
    conn.close()

    print(f"Sucesso! Tarefas processadas: {len(tasks)}")
    print(f"  - Novas inseridas: {inseridos}")
    print(f"  - Atualizadas: {atualizados}")

def main():
    caminho = localizar_arquivo()
    if not caminho:
        print("Erro: Não foi possível localizar o arquivo 3-temas_e_tasks.md em nenhum dos caminhos prováveis.")
        sys.exit(1)

    tasks = parse_markdown(caminho)
    if not tasks:
        print("Aviso: Nenhuma tarefa correspondente encontrada no arquivo markdown.")
        sys.exit(0)

    importar_para_db(tasks)

if __name__ == "__main__":
    main()
