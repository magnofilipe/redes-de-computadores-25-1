#!/bin/bash

# Script para testar o exemplo básico com 3 roteadores
echo "=== Testando Exemplo Básico ==="
echo "Iniciando 3 roteadores (A, B, C)..."

# Função para iniciar um roteador
start_router() {
    local name=$1
    local port=$2
    local config=$3
    local network=$4
    
    echo "Iniciando $name na porta $port..."
    python roteador.py -p $port -f $config --network $network --interval 5 &
    sleep 2
}

# Iniciar os roteadores
start_router "Roteador A" 5000 "exemplo/config_A.csv" "10.0.0.0/24"
start_router "Roteador B" 5001 "exemplo/config_B.csv" "10.0.1.0/24"
start_router "Roteador C" 5002 "exemplo/config_C.csv" "10.0.2.0/23"

echo ""
echo "Todos os roteadores foram iniciados!"
echo ""
echo "Para verificar as tabelas de roteamento, use:"
echo "curl http://localhost:5000/routes  # Roteador A"
echo "curl http://localhost:5001/routes  # Roteador B"
echo "curl http://localhost:5002/routes  # Roteador C"
echo ""
echo "Para testar uma atualização manual, use:"
echo "curl -X POST http://localhost:5001/receive_update \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{"
echo "    \"sender_address\": \"127.0.0.1:5000\","
echo "    \"routing_table\": {"
echo "      \"10.0.0.0/24\": { \"cost\": 0, \"next_hop\": \"10.0.0.0/24\" },"
echo "      \"10.0.1.0/24\": { \"cost\": 1, \"next_hop\": \"127.0.0.1:5001\" }"
echo "    }"
echo "  }'"
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
