#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Inicializador do Agente do Telegram
# ==============================================================================

AMARELO='\033[1;33m'
VERDE='\033[0;32m'
RESET='\033[0m'

echo -e "${AMARELO}[*] Iniciando o Agente do Telegram (Notas e Lembretes Diários)...${RESET}"
python3 "/mnt/c/principe/.system/S-Agentes/Agentes/telegram_agent.py"
