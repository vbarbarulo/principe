#!/usr/bin/env bash

# Define a pasta raiz do projeto
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== REINICIANDO HÓRUS SYSTEM ==="

# Executa o script de parada
bash "$BASE_DIR/stop.sh"

sleep 1

# Executa o script de início
bash "$BASE_DIR/start.sh"
