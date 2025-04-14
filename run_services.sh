#!/bin/bash

# Define variáveis para os arquivos de log
MAIN_LOG="./logs/main_app.log"
LOG_CONTROLLER_LOG="./logs/log_controller.log"

# Cria diretório de logs se não existir
mkdir -p ./logs

echo "Iniciando serviços PyWebLog em segundo plano..."

# Inicia o controlador de logs
echo "Iniciando serviço de controlador de logs..."
nohup python services/log_controller/app.py > "$LOG_CONTROLLER_LOG" 2>&1 &
LOG_CONTROLLER_PID=$!
echo "Controlador de logs iniciado com PID: $LOG_CONTROLLER_PID"

# Pequena pausa para garantir que o controlador de logs inicie primeiro
sleep 2

# Inicia o aplicativo principal
echo "Iniciando aplicativo principal..."
nohup python app.py > "$MAIN_LOG" 2>&1 &
MAIN_PID=$!
echo "Aplicativo principal iniciado com PID: $MAIN_PID"

# Salva os PIDs para uso posterior
echo "$LOG_CONTROLLER_PID" > ./logs/log_controller.pid
echo "$MAIN_PID" > ./logs/main_app.pid

echo "Ambos os serviços estão rodando em segundo plano"
echo "Para encerrar os serviços use: killall python"
echo "Logs disponíveis em: ./logs/"