#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Migração Local da Caixa de Entrada
# ==============================================================================

AMARELO='\033[1;33m'
VERDE='\033[0;32m'
RESET='\033[0m'

echo -e "${AMARELO}[*] Executando Migração Local da Caixa de Entrada...${RESET}"
python3 "/mnt/c/principe/.system/S-Agentes/Agentes/db_tarefas_migrator.py"
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] Migração local concluída com sucesso!${RESET}"
else
    echo -e "${VERDE}[-] Erro na migração local.${RESET}"
fi
