# -*- coding: utf-8 -*-

import csv
import json
import threading
import time
from argparse import ArgumentParser

import requests
from flask import Flask, jsonify, request

def ip_to_int(ip):
    """Converte um endereço IP para um inteiro de 32 bits."""
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

def int_to_ip(ip_int):
    """Converte um inteiro de 32 bits para um endereço IP."""
    return f"{(ip_int >> 24) & 255}.{(ip_int >> 16) & 255}.{(ip_int >> 8) & 255}.{ip_int & 255}"

def parse_network(network):
    """Extrai o IP e prefixo de uma rede no formato 'ip/prefixo'."""
    ip, prefix = network.split('/')
    return ip, int(prefix)

def can_summarize(network1, network2):
    """Verifica se duas redes podem ser sumarizadas."""
    ip1, prefix1 = parse_network(network1)
    ip2, prefix2 = parse_network(network2)
    
    # Só pode sumarizar redes com o mesmo prefixo
    if prefix1 != prefix2:
        return False, None
    
    # Converte para inteiros
    ip1_int = ip_to_int(ip1)
    ip2_int = ip_to_int(ip2)
    
    # Verifica se são adjacentes
    mask = (1 << (32 - prefix1)) - 1
    network1_addr = ip1_int & ~mask
    network2_addr = ip2_int & ~mask
    
    # Verifica se são adjacentes (diferença de exatamente um bloco de rede)
    if abs(network1_addr - network2_addr) == (1 << (32 - prefix1)):
        # Calcula a nova rede sumarizada
        if network1_addr < network2_addr:
            new_prefix = prefix1 - 1
            new_network = int_to_ip(network1_addr) + f"/{new_prefix}"
        else:
            new_prefix = prefix1 - 1
            new_network = int_to_ip(network2_addr) + f"/{new_prefix}"
        return True, new_network
    
    return False, None

def summarize_routes(routing_table):
    """Aplica sumarização de rotas na tabela de roteamento."""
    if len(routing_table) < 2:
        return routing_table
    
    # Cria uma cópia da tabela
    summarized_table = routing_table.copy()
    
    # Agrupa rotas por next_hop
    routes_by_next_hop = {}
    for network, route_info in summarized_table.items():
        if '/' not in network:
            continue
        next_hop = route_info['next_hop']
        if next_hop not in routes_by_next_hop:
            routes_by_next_hop[next_hop] = []
        routes_by_next_hop[next_hop].append((network, route_info))
    
    # Tenta sumarizar rotas para cada next_hop
    for next_hop, routes in routes_by_next_hop.items():
        if len(routes) < 2:
            continue
        
        # Ordena as redes para facilitar a busca por adjacentes
        routes.sort(key=lambda x: ip_to_int(parse_network(x[0])[0]))
        
        i = 0
        while i < len(routes) - 1:
            network1, route1 = routes[i]
            network2, route2 = routes[i + 1]
            
            can_sum, new_network = can_summarize(network1, network2)
            
            if can_sum:
                # Remove as duas redes originais
                del summarized_table[network1]
                del summarized_table[network2]
                
                # Adiciona a rede sumarizada
                max_cost = max(route1['cost'], route2['cost'])
                summarized_table[new_network] = {
                    'cost': max_cost,
                    'next_hop': next_hop
                }
                
                # Remove as rotas processadas da lista
                routes.pop(i)
                routes.pop(i)
                
                # Adiciona a nova rota sumarizada
                routes.insert(i, (new_network, {'cost': max_cost, 'next_hop': next_hop}))
                
                print(f"Sumarização: {network1} + {network2} -> {new_network}")
            else:
                i += 1
    
    return summarized_table

class Router:
    """
    Representa um roteador que executa o algoritmo de Vetor de Distância.
    """

    def __init__(self, my_address, neighbors, my_network, update_interval=1):
        """
        Inicializa o roteador.

        :param my_address: O endereço (ip:porta) deste roteador.
        :param neighbors: Um dicionário contendo os vizinhos diretos e o custo do link.
                          Ex: {'127.0.0.1:5001': 5, '127.0.0.1:5002': 10}
        :param my_network: A rede que este roteador administra diretamente.
                           Ex: '10.0.1.0/24'
        :param update_interval: O intervalo em segundos para enviar atualizações, o tempo que o roteador espera 
                                antes de enviar atualizações para os vizinhos.        """
        self.my_address = my_address
        self.neighbors = neighbors
        self.my_network = my_network
        self.update_interval = update_interval

        # Inicializa a tabela de roteamento
        self.routing_table = {}
        
        # Adiciona a rota para a rede local (custo 0)
        self.routing_table[self.my_network] = {
            'cost': 0,
            'next_hop': self.my_network
        }
        
        # Adiciona as rotas para os vizinhos diretos
        for neighbor_address, cost in self.neighbors.items():
            # Para vizinhos diretos, assumimos que eles administram suas próprias redes
            # Como não sabemos exatamente qual rede cada vizinho administra,
            # vamos criar uma entrada temporária que será atualizada quando recebermos
            # as informações deles
            self.routing_table[neighbor_address] = {
                'cost': cost,
                'next_hop': neighbor_address
            }

        print("Tabela de roteamento inicial:")
        print(json.dumps(self.routing_table, indent=4))

        # Inicia o processo de atualização periódica em uma thread separada
        self._start_periodic_updates()

    def _start_periodic_updates(self):
        """Inicia uma thread para enviar atualizações periodicamente."""
        thread = threading.Thread(target=self._periodic_update_loop)
        thread.daemon = True
        thread.start()

    def _periodic_update_loop(self):
        """Loop que envia atualizações de roteamento em intervalos regulares."""
        while True:
            time.sleep(self.update_interval)
            print(f"[{time.ctime()}] Enviando atualizações periódicas para os vizinhos...")
            try:
                self.send_updates_to_neighbors()
            except Exception as e:
                print(f"Erro durante a atualização periódida: {e}")

    def send_updates_to_neighbors(self):
        """
        Envia a tabela de roteamento para todos os vizinhos, aplicando
        a regra do Split Horizon.
        """

        time.sleep(3)

        dead_neighbors = []
        for neighbor_address in self.neighbors:
            # 1. Cria uma tabela personalizada para este vizinho específico
            tabela_personalizada = {}
            for network, route_info in self.routing_table.items():
                # A REGRA DO SPLIT HORIZON:
                # Só adiciona a rota na atualização se o próximo salto NÃO for o vizinho
                # para quem estamos enviando a mensagem.
                if route_info['next_hop'] != neighbor_address:
                    tabela_personalizada[network] = route_info
            
            # 2. Aplica sumarização na tabela já filtrada pelo Split Horizon
            tabela_para_enviar = summarize_routes(tabela_personalizada)

            payload = {
                "sender_address": self.my_address,
                "routing_table": tabela_para_enviar
            }

            url = f'http://{neighbor_address}/receive_update'
            try:
                # 3. Envia a tabela personalizada para o vizinho correto
                print(f"Enviando tabela (com Split Horizon) para {neighbor_address}")


                requests.post(url, json=payload, timeout=5)
            except requests.exceptions.RequestException as e:
                if "HTTPConnectionPool" in str(e):
                    porta = neighbor_address.split(':')[-1]
                    print(f"Roteador na porta {porta} está offline")
                    dead_neighbors.append(neighbor_address)

                print(f"Não foi possível conectar ao vizinho {neighbor_address}. Erro: {e}")

        for dead_neighbor in dead_neighbors:
            if dead_neighbor in self.neighbors:
                
                # Remove a entrada do vizinho morto da tabela de roteamento
                if dead_neighbor in self.routing_table:
                    print(f"Removendo entrada do vizinho morto da tabela: {dead_neighbor}")
                    del self.routing_table[dead_neighbor]
                
                # Remove também rotas que dependem deste vizinho
                routes_to_remove = []
                for network, route_info in self.routing_table.items():

                    if (route_info['next_hop'] == dead_neighbor and 
                        network != dead_neighbor and 
                        network not in self.neighbors):
                        routes_to_remove.append(network)
                
                for network in routes_to_remove:
                    print(f"Removendo rota órfã: {network}")
                    del self.routing_table[network]

# --- API Endpoints ---
# Instância do Flask e do Roteador (serão inicializadas no main)
app = Flask(__name__)
router_instance = None

@app.route('/routes', methods=['GET'])
def get_routes():
    """Endpoint para visualizar a tabela de roteamento atual."""
    if router_instance:
        return jsonify({
            "message": "Tabela de roteamento atual",
            "vizinhos": router_instance.neighbors,
            "my_network": router_instance.my_network,
            "my_address": router_instance.my_address,
            "update_interval": router_instance.update_interval,
            "routing_table": router_instance.routing_table
        })
    return jsonify({"error": "Roteador não inicializado"}), 500

@app.route('/receive_update', methods=['POST'])
def receive_update():
    """Endpoint que recebe atualizações de roteamento de um vizinho."""
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400

    update_data = request.json
    sender_address = update_data.get("sender_address")
    sender_table = update_data.get("routing_table")

    if not sender_address or not isinstance(sender_table, dict):
        return jsonify({"error": "Missing sender_address or routing_table"}), 400

    print(f"Recebida atualização de {sender_address}:")
    print(json.dumps(sender_table, indent=4))

    # Verifica se o remetente é um vizinho conhecido
    if sender_address not in router_instance.neighbors:
        print(f"Atualização recebida de {sender_address}, mas não é um vizinho conhecido")
        return jsonify({"status": "error", "message": "Unknown neighbor"}), 400
    
    # Obtém o custo do link direto para este vizinho
    direct_link_cost = router_instance.neighbors[sender_address]
    
    # Flag para verificar se a tabela mudou
    table_changed = False
    
    # Processa cada rota na tabela recebida
    for network, route_info in sender_table.items():

        if network == router_instance.my_address:
            continue
        # Calcula o novo custo para chegar à rede através deste vizinho
        new_cost = direct_link_cost + route_info['cost']
        
        # Verifica se já conhecemos esta rede
        if network in router_instance.routing_table:
            current_route = router_instance.routing_table[network]
            current_cost = current_route['cost']
            current_next_hop = current_route['next_hop']
            
            # Atualiza se o novo caminho for melhor OU se o next_hop for o sender
            if (new_cost < current_cost) or (current_next_hop == sender_address):
                if new_cost != current_cost or current_next_hop != sender_address:
                    router_instance.routing_table[network] = {
                        'cost': new_cost,
                        'next_hop': sender_address
                    }
                    table_changed = True
                    print(f"Rota atualizada: {network} -> custo {new_cost} via {sender_address}")
        else:
            # Nova rede descoberta
            router_instance.routing_table[network] = {
                'cost': new_cost,
                'next_hop': sender_address
            }
            table_changed = True
            print(f"Nova rota descoberta: {network} -> custo {new_cost} via {sender_address}")
    
    # Se a tabela mudou, imprime a nova tabela
    if table_changed:
        print("Nova tabela de roteamento:")
        print(json.dumps(router_instance.routing_table, indent=4))
    else:
        print("Tabela de roteamento não mudou")
        print(json.dumps(router_instance.routing_table, indent=4))

    return jsonify({"status": "success", "message": "Update received"}), 200

if __name__ == '__main__':
    parser = ArgumentParser(description="Simulador de Roteador com Vetor de Distância")
    parser.add_argument('-p', '--port', type=int, default=5000, help="Porta para executar o roteador.")
    parser.add_argument('-f', '--file', type=str, required=True, help="Arquivo CSV de configuração de vizinhos.")
    parser.add_argument('--network', type=str, required=True, help="Rede administrada por este roteador (ex: 10.0.1.0/24).")
    parser.add_argument('--interval', type=int, default=10, help="Intervalo de atualização periódica em segundos.")
    args = parser.parse_args()

    # Leitura do arquivo de configuração de vizinhos
    neighbors_config = {}
    try:
        with open(args.file, mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                neighbors_config[row['vizinho']] = int(row['custo'])
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração '{args.file}' não encontrado.")
        exit(1)
    except (KeyError, ValueError) as e:
        print(f"Erro no formato do arquivo CSV: {e}. Verifique as colunas 'vizinho' e 'custo'.")
        exit(1)

    my_full_address = f"127.0.0.1:{args.port}"
    print("--- Iniciando Roteador ---")
    print(f"Endereço: {my_full_address}")
    print(f"Rede Local: {args.network}")
    print(f"Vizinhos Diretos: {neighbors_config}")
    print(f"Intervalo de Atualização: {args.interval}s")
    print("--------------------------")

    router_instance = Router(
        my_address=my_full_address,
        neighbors=neighbors_config,
        my_network=args.network,
        update_interval=args.interval
    )

    # Inicia o servidor Flask
    app.run(host='0.0.0.0', port=args.port, debug=False)