#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Sincronização Completa de Minhas Tarefas
# ==============================================================================

AMARELO='\033[1;33m'
VERDE='\033[0;32m'
RESET='\033[0m'

echo -e "${AMARELO}[*] Executando Sincronização Completa de Minhas Tarefas...${RESET}"
python3 "/mnt/c/principe/S-Agentes/Agentes/asana_minhas_tarefas.py" --completo
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] Minhas Tarefas sincronizadas com sucesso!${RESET}"
else
    echo -e "${VERDE}[-] Erro na sincronização de Minhas Tarefas.${RESET}"
fi
