#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Gerenciador de Segundo Plano do Telegram Agent
# ==============================================================================

SCRIPT_PATH="/mnt/c/principe/S-Agentes/Agentes/telegram_agent.py"
LOG_PATH="/mnt/c/principe/S-Agentes/Agentes/telegram_agent.log"
PID_FILE="/mnt/c/principe/S-Agentes/Agentes/telegram_agent.pid"

AMARELO='\033[1;33m'
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
RESET='\033[0m'

get_pid() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "$PID"
            return 0
        fi
    fi
    # Busca alternativa pelo comando do processo
    PID=$(pgrep -f "python3 $SCRIPT_PATH")
    if [ ! -z "$PID" ]; then
        echo "$PID"
        return 0
    fi
    echo ""
    return 1
}

start_agent() {
    PID=$(get_pid)
    if [ ! -z "$PID" ]; then
        echo -e "${AMARELO}[*] O Agente do Telegram já está rodando em segundo plano (PID: $PID).${RESET}"
        return 0
    fi

    echo -e "${AMARELO}[*] Iniciando o Agente do Telegram em segundo plano...${RESET}"
    nohup python3 -u "$SCRIPT_PATH" > "$LOG_PATH" 2>&1 &
    NEW_PID=$!
    
    echo "$NEW_PID" > "$PID_FILE"
    sleep 1
    
    if ps -p "$NEW_PID" > /dev/null 2>&1; then
        echo -e "${VERDE}[+] Agente iniciado com sucesso! (PID: $NEW_PID)${RESET}"
        echo -e "${VERDE}[+] Logs sendo gravados em: $LOG_PATH${RESET}"
    else
        echo -e "${VERMELHO}[-] Erro ao iniciar o agente. Verifique os logs em $LOG_PATH${RESET}"
    fi
}

stop_agent() {
    PID=$(get_pid)
    if [ -z "$PID" ]; then
        echo -e "${AMARELO}[*] O Agente do Telegram não está rodando.${RESET}"
        return 0
    fi

    echo -e "${AMARELO}[*] Parando o Agente do Telegram (PID: $PID)...${RESET}"
    kill "$PID"
    sleep 1
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${AMARELO}[*] Forçando parada com kill -9...${RESET}"
        kill -9 "$PID"
    fi
    
    rm -f "$PID_FILE"
    echo -e "${VERDE}[+] Agente parado com sucesso!${RESET}"
}

status_agent() {
    PID=$(get_pid)
    if [ ! -z "$PID" ]; then
        echo -e "${VERDE}[+] O Agente do Telegram está ATIVO e rodando em segundo plano (PID: $PID).${RESET}"
        echo -e "[*] Últimas 5 linhas de log:"
        tail -n 5 "$LOG_PATH"
    else
        echo -e "${VERMELHO}[-] O Agente do Telegram está INATIVO.${RESET}"
    fi
}

case "$1" in
    start)
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    status)
        status_agent
        ;;
    restart)
        stop_agent
        sleep 1
        start_agent
        ;;
    *)
        echo "Uso: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
