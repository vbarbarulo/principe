import os

def load_env():
    """
    Carrega variáveis de ambiente a partir do arquivo .env na raiz do projeto.
    Garante suporte nativo sem dependências externas.
    """
    # Encontra a pasta raiz de forma dinâmica (subindo 3 níveis a partir de src/utils/env_loader.py)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, ".env")
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    # Define no ambiente se já não estiver definido
                    k = key.strip()
                    v = val.strip().strip('"').strip("'")
                    os.environ[k] = v
