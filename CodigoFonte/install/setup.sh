#!/bin/bash
# Script de Instalação Rápida para o Sargento IA do Zero

echo "=== INICIANDO INSTALAÇÃO DO SARGENTO IA ==="
echo "Passo 1: Atualizando pacotes..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv sqlite3 zip

echo "Passo 2: Instalando as dependências do Python..."
pip3 install python-telegram-bot apscheduler requests google-generativeai

echo "Passo 3: Baixando e instalando o Ollama local no WSL..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Passo 4: Puxando o modelo de IA leve e focado (Llama 3)..."
ollama pull llama3

echo "Passo 5: Inicializando o banco de dados..."
python3 ../src/database/database.py

echo "=== INSTALAÇÃO CONCLUÍDA COM SUCESSO! ==="
echo "Para rodar o bot, use: python3 ../src/bot.py"
