import os
import sys
import zipfile
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

def create_backup():
    db_path = os.path.join(ROOT_DIR, "data", "agent.db")
    config_dir = os.path.join(ROOT_DIR, "config")
    backup_dir = os.path.join(ROOT_DIR, "exports", "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"horus_backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)

    print(f"Iniciando backup local do Hórus QG...")

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Copia o banco de dados principal
            if os.path.exists(db_path):
                zipf.write(db_path, "agent.db")
                print("✔ agent.db adicionado ao pacote.")
            
            # 2. Copia a pasta de configurações
            if os.path.exists(config_dir):
                for root, dirs, files in os.walk(config_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, ROOT_DIR)
                        zipf.write(file_path, arcname)
                print("✔ Pasta config/ adicionada ao pacote.")

        print(f"🎉 Backup concluído com sucesso!")
        print(f"📦 Salvo em: {backup_path}")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {str(e)}")

if __name__ == "__main__":
    create_backup()
