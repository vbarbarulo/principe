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

echo "=== STATUS DO HÓRUS SYSTEM ==="

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🟢 O Bot está ATIVO e rodando em segundo plano!"
        echo "📌 PID do processo: $PID"
        echo "🕒 Tempo de execução ativo:"
        ps -o etime= -p "$PID"
    else
        echo "🔴 O Bot está INATIVO (o arquivo PID existe, mas o processo não está rodando)."
    fi
else
    # Procura por processos em geral
    PID=$(pgrep -f "python3.*(src/)?bot.py")
    if [ -n "$PID" ]; then
        echo "🟢 O Bot está ATIVO (encontrado via busca de processos)!"
        echo "📌 PIDs: $PID"
    else
        echo "🔴 O Bot está INATIVO."
    fi
fi

if [ -f "$LOG_FILE" ]; then
    echo -e "\n📄 Últimas 10 linhas do log ($LOG_FILE):"
    echo "--------------------------------------------------"
    tail -n 10 "$LOG_FILE"
    echo "--------------------------------------------------"
else
    echo -e "\n📄 Nenhum arquivo de log encontrado em $LOG_FILE"
fi
