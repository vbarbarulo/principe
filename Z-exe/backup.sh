#!/usr/bin/env bash

# Define a pasta raiz do projeto
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_ROOT="$(cd "$BASE_DIR/../.." && pwd)"
SRC_DIR="$PROJ_ROOT/CodigoFonte"

echo "=== CRIANDO BACKUP DO SISTEMA ==="
python3 "$SRC_DIR/scripts/backup.py"
