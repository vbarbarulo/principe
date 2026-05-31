#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ==============================================================================
# Horus System - Sincronização Geral Completa
# Executa a rotina completa de download e sincronização para todos os 4 agentes.
# ==============================================================================

# Define cores para logs elegantes no terminal
VERDE='\033[0;32m'
AZUL='\033[0;34m'
AMARELO='\033[1;33m'
RESET='\033[0m'

echo -e "${AZUL}======================================================================${RESET}"
echo -e "${AZUL}       INICIANDO ROTINA INTEGRAL DE SINCRONIZAÇÃO - HÓRUS SYSTEM      ${RESET}"
echo -e "${AZUL}======================================================================${RESET}"
date
echo ""

# Caminho da pasta de Agentes
AGENTES_DIR="/mnt/c/principe/.system/Automações"

# 1. Executa o Agente de OKRs (Completo)
echo -e "${AMARELO}[1/4] Executando Sincronização Completa de OKRs...${RESET}"
python3 "${AGENTES_DIR}/asana_okr_agent.py" --completo
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] OKRs sincronizados com sucesso!${RESET}\n"
else
    echo -e "${VERDE}[-] Falha na sincronização de OKRs.${RESET}\n"
fi

# 2. Executa o Agente de Prioridades e Custos (Completo)
echo -e "${AMARELO}[2/4] Executando Sincronização Completa de Prioridades e Custos...${RESET}"
python3 "${AGENTES_DIR}/asana_prioridades_agent.py" --completo
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] Prioridades e Custos sincronizados com sucesso!${RESET}\n"
else
    echo -e "${VERDE}[-] Falha na sincronização de Prioridades e Custos.${RESET}\n"
fi

# 3. Executa o Agente de Minhas Tarefas (Completo)
echo -e "${AMARELO}[3/4] Executando Sincronização Completa de Minhas Tarefas...${RESET}"
python3 "${AGENTES_DIR}/asana_minhas_tarefas.py" --completo
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] Minhas Tarefas sincronizadas com sucesso!${RESET}\n"
else
    echo -e "${VERDE}[-] Falha na sincronização de Minhas Tarefas.${RESET}\n"
fi

# 4. Executa o Migrador da Caixa de Entrada Local (Tarefas ➡️ FuturoGestão)
echo -e "${AMARELO}[4/4] Executando Migração Local da Caixa de Entrada...${RESET}"
python3 "${AGENTES_DIR}/db_tarefas_migrator.py"
if [ $? -eq 0 ]; then
    echo -e "${VERDE}[+] Migração local concluída com sucesso!${RESET}\n"
else
    echo -e "${VERDE}[-] Falha na migração local.${RESET}\n"
fi

echo -e "${AZUL}======================================================================${RESET}"
echo -e "${VERDE}      ROTINA GERAL FINALIZADA COM SUCESSO - DADOS ATUALIZADOS!        ${RESET}"
echo -e "${AZUL}======================================================================${RESET}"
date
