# Grupo 7 - Implementação do Protocolo de Roteamento Vetor de Distância

## Visão Geral

Este projeto implementa um simulador de roteador que executa o algoritmo de **Vetor de Distância (Distance Vector)** com suporte a **sumarização de rotas**.

## Estrutura do Projeto

## Topologia Implementada

A topologia escolhida por nós é uma **árvore** com 12 roteadores organizados em 4 níveis:

- **R1**: roteador raiz.
- **R2, R3**: primeiro nível de filhos.
- **R4, R5, R6, R7**: segundo nível de filhos.
- **R8, R9, R10, R11, R12**: terceiro nível (folhas).

### Características da Topologia

1. **Estrutura Hierárquica**: cada roteador tem no máximo um pai.
2. **Custos**: links com custos 1 e 2 para testar convergência.
3. **Sumarização**: toda estrutura para demonstrar.
4. **Convergência**: rápida, esperada em poucos ciclos.

## Funcionalidades Implementadas

### Algoritmo de Vetor de Distância
Implementação do algoritmo Bellman-Ford, atualização automática de tabelas de roteamento, detecção de rotas de menor custo e convergência automática.

### Sumarização de Rotas
Agregação de redes adjacentes com mesmo next_hop, cálculo automático de super-redes, otimização de anúncios de rota, além da implementação sem bibliotecas externas.

### API REST
- Endpoint `/routes` para visualizar tabelas.
- Endpoint `/receive_update` para receber atualizações.
- Formato JSON padronizado.

## Como Testar

### 1. Teste Básico (3 Roteadores)

```bash
# No diretório roteamento/
./testar_exemplo.sh
```

Este comando inicia os 3 roteadores do exemplo básico (A, B, C).

### 2. Teste Completo (12 Roteadores)

```bash
# No diretório roteamento/
./grupo7/testar_topologia.sh
```

Este comando inicia todos os 12 roteadores da topologia Tree.

### 3. Teste Manual

Para testar manualmente, execute em terminais separados:

```bash
# Terminal 1 - R1 (Raiz)
python roteador.py -p 5001 -f grupo7/R1.csv --network 10.0.1.0/24

# Terminal 2 - R2
python roteador.py -p 5002 -f grupo7/R2.csv --network 10.0.2.0/24

# ... e assim por diante para os outros roteadores
```

### 4. Verificar Tabelas de Roteamento

```bash
# Verificar tabela do R1
curl http://localhost:5001/routes

# Verificar tabela do R2
curl http://localhost:5002/routes

# ... e assim por diante
```

### 5. Teste de Atualização Manual

```bash
curl -X POST http://localhost:5002/receive_update \
  -H "Content-Type: application/json" \
  -d '{
    "sender_address": "192.168.0.1:5001",
    "routing_table": {
      "10.0.1.0/24": { "cost": 0, "next_hop": "10.0.1.0/24" },
      "10.0.2.0/24": { "cost": 1, "next_hop": "192.168.0.2:5002" }
    }
  }'
```

## Comandos Úteis

### Parar Todos os Roteadores
```bash
pkill -f roteador.py
```

### Verificar Processos Ativos
```bash
ps aux | grep roteador.py
```

### Testar Conectividade
```bash
# Testar se um roteador está respondendo
curl http://localhost:5001/routes
```

### Capturar Tráfego com Wireshark
```bash
# Filtrar apenas tráfego HTTP
http

# Filtrar apenas POST requests
http.request.method == "POST"
```

## Troubleshooting

### Problema: Porta já em uso
```bash
# Encontrar processo usando a porta
lsof -i :5001

# Matar o processo
kill -9 <PID>
```
