#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Sincronização Completa de Prioridades e Custos
# ==============================================================================

AMARELO='\033[1;33m'
VERDE='\033[0;32m'
RESET='\033[0m'

echo -e "${AMARELO}[*] Executando Sincronização Completa de Prioridades e Custos...${RESET}"
python3 "/mnt/c/principe/.system/Automações/asana_prioridades_agent.py" --completo
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] Prioridades e Custos sincronizados com sucesso!${RESET}"
else
    echo -e "${VERDE}[-] Erro na sincronização de Prioridades e Custos.${RESET}"
fi
