#!/bin/bash
echo "Derrubando processos ativos do bot.py no WSL..."
pkill -f "python3.*bot.py"
sleep 2
echo "Iniciando bot do Telegram em segundo plano..."
nohup python3 "$(dirname "$0")/../src/bot.py" > horus_bot.log 2>&1 &
echo "Bot reiniciado com sucesso! Logs salvos em horus_bot.log"
