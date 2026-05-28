import os
import re

class RotinasParser:
    def __init__(self, filepath=None):
        if filepath is None:
            # Caminho padrão
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "rotinas.md")
        self.filepath = filepath

    def parse(self):
        """
        Lê o arquivo rotinas.md e extrai os blocos, tarefas e sub-tarefas.
        Gera IDs estáveis para cada tarefa/sub-tarefa.
        """
        if not os.path.exists(self.filepath):
            return {}

        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        rotinas = {}
        current_block = None
        current_block_id = None
        current_block_time = None
        task_counter = 0
        subtask_counter = 0
        last_task_id = None

        # Mapeamento manual amigável para IDs de bloco com base no título
        block_id_mapping = {
            "acordar": "acordar",
            "café": "cafe",
            "trabalho": "trabalho",
            "meio dia": "meio_dia",
            "arrumar a casa": "arrumar_casa",
            "início da noite": "inicio_noite",
            "finalização da noite": "finalizacao_noite"
        }

        for line in lines:
            # Detecta blocos: ## 🌅 Rotina Acordar [06:00]
            block_match = re.match(r"^##\s+(?:[^\w\s]+)?\s*(Rotina[^\s]*\s+[^\[]+)\s*\[(\d{2}:\d{2})\]", line, re.IGNORECASE)
            if not block_match:
                # Fallback genérico para ## [Título] [HH:MM]
                block_match = re.match(r"^##\s+(.*?)\s*\[(\d{2}:\d{2})\]", line)

            if block_match:
                block_title = block_match.group(1).strip()
                current_block_time = block_match.group(2).strip()
                
                # Identificar ID do bloco
                block_clean = block_title.lower()
                current_block_id = "bloco_generico"
                for key, val in block_id_mapping.items():
                    if key in block_clean:
                        current_block_id = val
                        break
                
                current_block = {
                    "id": current_block_id,
                    "titulo": block_title,
                    "horario": current_block_time,
                    "tarefas": []
                }
                rotinas[current_block_id] = current_block
                task_counter = 0
                last_task_id = None
                continue

            if current_block is None:
                continue

            # Detecta sub-tarefas (indentadas com tab ou 4 espaços e começadas com - [ ] ou -)
            subtask_match = re.match(r"^(?:\t|\s{2,})[-*]\s+\[\s*\]\s+(.+)$", line)
            if not subtask_match:
                subtask_match = re.match(r"^(?:\t|\s{2,})[-*]\s+(.+)$", line)

            if subtask_match and last_task_id:
                subtask_text = subtask_match.group(1).strip()
                subtask_counter += 1
                subtask_id = f"{last_task_id}_{subtask_counter:02d}"
                
                # Procura a tarefa principal para adicionar a sub-tarefa
                for task in current_block["tarefas"]:
                    if task["id"] == last_task_id:
                        if "subtarefas" not in task:
                            task["subtarefas"] = []
                        task["subtarefas"].append({
                            "id": subtask_id,
                            "texto": subtask_text
                        })
                continue

            # Detecta tarefas principais (- [ ] ou -)
            task_match = re.match(r"^[-*]\s+\[\s*\]\s+(.+)$", line)
            if not task_match:
                task_match = re.match(r"^[-*]\s+(.+)$", line)

            if task_match:
                task_text = task_match.group(1).strip()
                task_counter += 1
                task_id = f"{current_block_id}_{task_counter:02d}"
                last_task_id = task_id
                subtask_counter = 0
                
                current_block["tarefas"].append({
                    "id": task_id,
                    "texto": task_text,
                    "subtarefas": []
                })

        return rotinas

if __name__ == "__main__":
    parser = RotinasParser()
    res = parser.parse()
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
