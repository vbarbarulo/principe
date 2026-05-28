#!/usr/bin/env bash

# Define a pasta raiz do projeto de forma dinâmica
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -d "$BASE_DIR/CodigoFonte" ]; then
    PROJ_ROOT="$BASE_DIR"
else
    PROJ_ROOT="$(cd "$BASE_DIR/../.." && pwd)"
fi
SRC_DIR="$PROJ_ROOT/CodigoFonte"

PID_FILE="$SRC_DIR/.bot.pid"
LOG_FILE="$SRC_DIR/data/bot.log"

echo "=== INICIANDO HÓRUS SYSTEM (SARGENTO IA) ==="

# Verifica se o bot já está rodando
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️ O bot já está rodando com o PID: $PID"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Checa se há algum processo residual rodando e limpa
RESIDUAL_PID=$(pgrep -f "python3.*(src/)?bot.py")
if [ -n "$RESIDUAL_PID" ]; then
    echo "⚠️ Detectado processo residual rodando (PIDs: $RESIDUAL_PID). Limpando..."
    pkill -f "python3.*(src/)?bot.py"
    sleep 1
fi

echo "🚀 Iniciando bot.py em segundo plano..."
cd "$SRC_DIR"
nohup python3 src/bot.py >> "$LOG_FILE" 2>&1 &

# Captura e salva o PID
BOT_PID=$!
echo "$BOT_PID" > "$PID_FILE"

# Inicia o Obsidian automaticamente em segundo plano se não estiver aberto
if ! pgrep -x "obsidian" > /dev/null; then
    echo "📓 Abrindo o Obsidian..."
    obsidian --no-sandbox > /dev/null 2>&1 &
fi

echo "✔ Bot e Obsidian iniciados com sucesso!"
echo "📌 PID do Bot: $BOT_PID"
echo "📄 Logs sendo salvos em: $LOG_FILE"
echo "💪 Persistência ativada. Você já pode fechar este terminal!"
