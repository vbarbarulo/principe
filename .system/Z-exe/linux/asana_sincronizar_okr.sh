#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Sincronização Completa de OKRs
# ==============================================================================

AMARELO='\033[1;33m'
VERDE='\033[0;32m'
RESET='\033[0m'

echo -e "${AMARELO}[*] Executando Sincronização Completa de OKRs...${RESET}"
python3 "/mnt/c/principe/.system/S-Agentes/Agentes/asana_okr_agent.py" --completo
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] OKRs sincronizados com sucesso!${RESET}"
else
    echo -e "${VERDE}[-] Erro na sincronização de OKRs.${RESET}"
fi
