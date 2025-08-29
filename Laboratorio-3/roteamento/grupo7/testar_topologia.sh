#!/bin/bash

# Script para testar a topologia do Grupo 7
# Topologia Tree com 12 roteadores

echo "=== Testando Topologia Tree - Grupo 7 ==="
echo "Iniciando 12 roteadores em terminais separados..."
echo ""

# Função para iniciar um roteador em background
start_router() {
    local router_num=$1
    local network=$2
    local port=$3
    
    echo "Iniciando R$router_num na porta $port..."
    python roteador.py -p $port -f grupo7/R$router_num.csv --network $network --interval 5 &
    sleep 1
}

# Iniciar todos os roteadores
echo "Iniciando roteadores..."

# R1 (Raiz) - porta 5001
start_router 1 "10.0.1.0/24" 5001

# R2 - porta 5002
start_router 2 "10.0.2.0/24" 5002

# R3 - porta 5003
start_router 3 "10.0.3.0/24" 5003

# R4 - porta 5004
start_router 4 "10.0.4.0/24" 5004

# R5 - porta 5005
start_router 5 "10.0.5.0/24" 5005

# R6 - porta 5006
start_router 6 "10.0.6.0/24" 5006

# R7 - porta 5007
start_router 7 "10.0.7.0/24" 5007

# R8 - porta 5008
start_router 8 "10.0.8.0/24" 5008

# R9 - porta 5009
start_router 9 "10.0.9.0/24" 5009

# R10 - porta 5010
start_router 10 "10.0.10.0/24" 5010

# R11 - porta 5011
start_router 11 "10.0.11.0/24" 5011

# R12 - porta 5012
start_router 12 "10.0.12.0/24" 5012

echo ""
echo "Todos os roteadores foram iniciados!"
echo ""
echo "Para verificar as tabelas de roteamento, use:"
echo "curl http://localhost:5001/routes  # R1"
echo "curl http://localhost:5002/routes  # R2"
echo "curl http://localhost:5003/routes  # R3"
echo "..."
echo ""
echo "Para parar todos os roteadores, use: pkill -f roteador.py"
echo ""
echo "Pressione Ctrl+C para parar este script"
echo ""

# Aguardar indefinidamente
while true; do
    sleep 10
    echo "Roteadores ainda rodando... (Ctrl+C para parar)"
done
