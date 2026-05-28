#!/usr/bin/env bash

# Define a pasta raiz do projeto
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_ROOT="$(cd "$BASE_DIR/../.." && pwd)"
SRC_DIR="$PROJ_ROOT/CodigoFonte"

echo "================================================================="
echo "   🚀 INSTALAÇÃO COMPLETA: SARGENTO IA & OBSIDIAN (WSL)   "
echo "================================================================="

# 1. Atualização do Sistema e Instalação de Ferramentas Base
echo "🔄 Passo 1: Atualizando repositórios e instalando dependências base..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv sqlite3 git curl wget libasound2 libgbm1 libxss1 libnss3 xdg-utils

# 2. Instalação do Obsidian Nativo no WSL (WSLg)
if ! command -v obsidian &> /dev/null; then
    echo "📥 Passo 2: Baixando e instalando Obsidian para Linux/WSL (WSLg)..."
    OBSIDIAN_URL="https://github.com/obsidianmd/obsidian-releases/releases/download/v1.6.7/obsidian_1.6.7_amd64.deb"
    wget -q --show-progress -O /tmp/obsidian.deb "$OBSIDIAN_URL"
    
    echo "📦 Instalando pacote do Obsidian..."
    sudo apt install -y /tmp/obsidian.deb
    rm /tmp/obsidian.deb
    echo "✔ Obsidian instalado com sucesso!"
else
    echo "✔ Passo 2: Obsidian já está instalado!"
fi

# 3. Instalação de Dependências Python
echo "📦 Passo 3: Instalando as dependências do Python..."
python3 -m pip install --upgrade pip --break-system-packages 2>/dev/null || python3 -m pip install --upgrade pip

if [ -f "$SRC_DIR/install/requirements.txt" ]; then
    python3 -m pip install --break-system-packages -r "$SRC_DIR/install/requirements.txt" 2>/dev/null || python3 -m pip install -r "$SRC_DIR/install/requirements.txt"
else
    echo "⚠️ requirements.txt não encontrado no caminho padrão. Instalando principais pacotes..."
    python3 -m pip install --break-system-packages python-telegram-bot apscheduler requests google-generativeai openai 2>/dev/null || pip3 install python-telegram-bot apscheduler requests google-generativeai openai
fi

# 4. Inicialização do Banco de Dados
echo "🗄️ Passo 4: Inicializando o banco de dados local (SQLite)..."
if [ -f "$SRC_DIR/src/database/database.py" ]; then
    python3 "$SRC_DIR/src/database/database.py"
else
    echo "⚠️ Arquivo database.py não encontrado no caminho esperado!"
fi

echo "================================================================="
echo "🎉 INSTALAÇÃO E ATUALIZAÇÃO CONCLUÍDAS COM SUCESSO! 🎉"
echo "================================================================="
echo "💡 Para rodar o bot/agente em segundo plano, execute:"
echo "   ./start.sh"
echo ""
echo "💡 Para abrir o Obsidian diretamente do WSL:"
echo "   obsidian &"
echo "================================================================="

