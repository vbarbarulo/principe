import os
import sys
import sqlite3
from datetime import datetime, date

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.database.upsert_engine import DB_PATH

class ObsidianSync:
    def __init__(self, vault_path=None):
        if vault_path is None:
            # Por padrão, usa a pasta diarios/ do próprio projeto como Vault
            vault_path = os.path.join(ROOT_DIR, "diarios")
        self.vault_path = vault_path
        os.makedirs(self.vault_path, exist_ok=True)

    def sync_day(self, data_str=None):
        """
        Gera um relatório diário completo em Markdown contendo Frontmatter YAML
        integrando as tabelas registros_rotina, itens_segundo_cerebro e logs_descompressao.
        """
        if data_str is None:
            data_str = date.today().isoformat()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Busca rotinas do dia
        cursor.execute("SELECT rotina_id, acoes_concluidas, acoes_puladas, dados_capturados, status FROM registros_rotina WHERE data = ?", (data_str,))
        rotinas = cursor.fetchall()

        # 2. Busca itens do segundo cérebro (tarefas, notas) do dia
        cursor.execute("SELECT id, tipo, curva, tempo, conteudo, tags FROM itens_segundo_cerebro WHERE data_registro = ?", (data_str,))
        itens = cursor.fetchall()

        # 3. Busca logs de descompressão do dia
        cursor.execute("SELECT conteudo_bruto, analise_ia, decisoes_tomadas FROM logs_descompressao WHERE data = ?", (data_str,))
        descompressoes = cursor.fetchall()

        # 4. Compila YAML Frontmatter
        kpis = {}
        peso = None
        for r in rotinas:
            kpis[r[0]] = r[4]
            # Extrai peso dos dados capturados se houver
            try:
                import json
                capturas = json.loads(r[3]) if r[3] else {}
                if "peso_kg" in capturas:
                    peso = capturas["peso_kg"]
            except Exception:
                pass

        yaml_lines = [
            "---",
            f"data: {data_str}",
            f"peso_kg: {peso if peso else 'null'}",
        ]
        for key, val in kpis.items():
            yaml_lines.append(f"kpi_{key}: {val}")
        yaml_lines.append("---")

        # 5. Monta o corpo Markdown
        md = []
        md.append("\n".join(yaml_lines))
        md.append(f"\n# Relatório Diário Hórus - {data_str}\n")

        # Seção Rotinas
        md.append("## 🕒 Estado das Microrrotinas Diárias")
        if rotinas:
            for r in rotinas:
                import json
                concluidas = json.loads(r[1]) if r[1] else []
                puladas = json.loads(r[2]) if r[2] else []
                md.append(f"\n### ➔ Bloco: **{r[0].upper()}** (Status: *{r[4]}*)")
                md.append(f"- ✅ **Concluídas ({len(concluidas)}):** {', '.join([x.split('_')[-1] for x in concluidas]) if concluidas else 'Nenhuma'}")
                md.append(f"- 💤 **Puladas ({len(puladas)}):** {', '.join([x.split('_')[-1] for x in puladas]) if puladas else 'Nenhuma'}")
        else:
            md.append("\n*Nenhum log de rotina registrado hoje.*")

        # Seção Segundo Cérebro (Curva ABC)
        md.append("\n## 🧠 Itens do Segundo Cérebro (Classificação ABC)")
        if itens:
            for item in itens:
                import json
                tags_list = json.loads(item[5]) if item[5] else []
                tags_fmt = " ".join([f"#{t}" for t in tags_list])
                md.append(f"- [{item[2]}] **[{item[1].upper()}]** {item[4]} {tags_fmt}")
        else:
            md.append("\n*Nenhuma tarefa ou insight registrado para o cérebro hoje.*")

        # Seção Descompressão
        md.append("\n## 📝 Relato e Descompressão Ativa")
        if descompressoes:
            for d in descompressoes:
                md.append(f"\n> {d[0]}")
                md.append(f"\n🤖 **Análise da IA:**\n{d[1]}")
                if d[2]:
                    md.append(f"\n💡 **Lições/Decisões:**\n{d[2]}")
        else:
            md.append("\n*Nenhuma descompressão realizada hoje.*")

        # Grava o arquivo Markdown
        filename = f"relatorio_{data_str}.md"
        filepath = os.path.join(self.vault_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        # Atualiza o status dos itens no banco para sincronizado
        for item in itens:
            cursor.execute("UPDATE itens_segundo_cerebro SET status = 'sincronizado_obsidian' WHERE id = ?", (item[0],))

        conn.commit()
        conn.close()
        return filepath

if __name__ == "__main__":
    sync = ObsidianSync()
    path = sync.sync_day()
    print(f"Sincronização executada com sucesso! Arquivo gerado: {path}")
