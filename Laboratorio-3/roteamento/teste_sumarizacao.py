#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import requests
import json

def test_summarization():
    """Testa a funcionalidade de sumarização de rotas"""
    
    print("=== Teste de Sumarização de Rotas ===")
    
    # Inicia o roteador em background
    print("Iniciando roteador...")
    process = subprocess.Popen([
        'python', 'roteador.py', 
        '-p', '5000', 
        '-f', 'exemplo/config_A.csv', 
        '--network', '10.0.0.0/24',
        '--interval', '5'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Aguarda um pouco para o roteador inicializar
    time.sleep(3)
    
    try:
        # Adiciona várias rotas que podem ser sumarizadas
        print("Adicionando rotas para testar sumarização...")
        
        # Rotas que podem ser sumarizadas (10.0.1.0/24, 10.0.2.0/24 -> 10.0.0.0/22)
        update_data = {
            "sender_address": "127.0.0.1:5001",
            "routing_table": {
                "10.0.1.0/24": {"cost": 0, "next_hop": "10.0.1.0/24"},
                "10.0.2.0/24": {"cost": 0, "next_hop": "10.0.2.0/24"},
                "10.0.3.0/24": {"cost": 0, "next_hop": "10.0.3.0/24"},
                "10.0.4.0/24": {"cost": 0, "next_hop": "10.0.4.0/24"},
                "192.168.1.0/24": {"cost": 1, "next_hop": "127.0.0.1:5001"},
                "192.168.2.0/24": {"cost": 1, "next_hop": "127.0.0.1:5001"}
            }
        }
        
        response = requests.post(
            'http://localhost:5000/receive_update',
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Rotas adicionadas com sucesso!")
            
            # Verifica a tabela atual
            response = requests.get('http://localhost:5000/routes', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("Tabela de roteamento após adição das rotas:")
                print(json.dumps(data['routing_table'], indent=2))
                
                # Verifica se há sumarização
                print("\nVerificando sumarização...")
                routes = data['routing_table']
                
                # Procura por rotas sumarizadas
                summarized_routes = []
                for network, route_info in routes.items():
                    if '/' in network:
                        parts = network.split('/')
                        if len(parts) == 2:
                            prefix = int(parts[1])
                            if prefix < 24:  # Rotas sumarizadas têm prefixo menor
                                summarized_routes.append(network)
                
                if summarized_routes:
                    print("✅ Rotas sumarizadas encontradas:")
                    for route in summarized_routes:
                        print(f"  - {route}: {routes[route]}")
                else:
                    print("ℹ️ Nenhuma rota sumarizada encontrada (pode ser normal)")
                
        else:
            print(f"❌ Erro ao adicionar rotas: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao roteador")
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    finally:
        # Para o processo
        process.terminate()
        process.wait()
        print("Roteador parado.")

if __name__ == '__main__':
    test_summarization()
