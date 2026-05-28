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

echo "=== PARANDO HÓRUS SYSTEM (SARGENTO IA) ==="

# Tenta parar pelo arquivo PID primeiro
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Parando processo do bot (PID: $PID)..."
        kill "$PID"
        sleep 2
        
        # Se ainda estiver vivo, força a parada
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️ O processo não respondeu. Forçando encerramento (kill -9)..."
            kill -9 "$PID"
        fi
    else
        echo "ℹ️ Processo do PID $PID não encontrado."
    fi
    rm "$PID_FILE"
fi

# Garante limpando qualquer outro processo python3 bot.py residual
RESIDUAL_PID=$(pgrep -f "python3.*(src/)?bot.py")
if [ -n "$RESIDUAL_PID" ]; then
    echo "🛑 Finalizando outros processos residuais do bot (PIDs: $RESIDUAL_PID)..."
    pkill -f "python3.*(src/)?bot.py"
    sleep 1
fi

echo "✔ Bot parado com sucesso."
