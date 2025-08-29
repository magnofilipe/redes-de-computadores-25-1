#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import requests
import json
import threading

def start_router(port, config_file, network, name):
    """Inicia um roteador em uma thread separada"""
    print(f"Iniciando {name} na porta {port}...")
    process = subprocess.Popen([
        'python', 'roteador.py', 
        '-p', str(port), 
        '-f', config_file, 
        '--network', network,
        '--interval', '3'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def get_routing_table(port, name):
    """Obtém a tabela de roteamento de um roteador"""
    try:
        response = requests.get(f'http://localhost:{port}/routes', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n=== Tabela de Roteamento - {name} ===")
            print(json.dumps(data['routing_table'], indent=2))
            return data['routing_table']
        else:
            print(f"❌ Erro ao obter tabela de {name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao conectar com {name}: {e}")
        return None

def test_complete_example():
    """Testa o exemplo completo com 3 roteadores"""
    
    print("=== Teste do Exemplo Completo (3 Roteadores) ===")
    
    # Inicia os 3 roteadores
    processes = []
    
    # Roteador A
    process_a = start_router(5000, 'exemplo/config_A.csv', '10.0.0.0/24', 'Roteador A')
    processes.append(('A', process_a))
    
    # Roteador B
    process_b = start_router(5001, 'exemplo/config_B.csv', '10.0.1.0/24', 'Roteador B')
    processes.append(('B', process_b))
    
    # Roteador C
    process_c = start_router(5002, 'exemplo/config_C.csv', '10.0.2.0/23', 'Roteador C')
    processes.append(('C', process_c))
    
    # Aguarda inicialização
    time.sleep(5)
    
    try:
        print("\n=== Estado Inicial ===")
        
        # Obtém tabelas iniciais
        table_a = get_routing_table(5000, 'Roteador A')
        table_b = get_routing_table(5001, 'Roteador B')
        table_c = get_routing_table(5002, 'Roteador C')
        
        # Aguarda algumas atualizações
        print("\n=== Aguardando convergência (15 segundos) ===")
        time.sleep(15)
        
        print("\n=== Estado Após Convergência ===")
        
        # Obtém tabelas após convergência
        table_a_final = get_routing_table(5000, 'Roteador A')
        table_b_final = get_routing_table(5001, 'Roteador B')
        table_c_final = get_routing_table(5002, 'Roteador C')
        
        # Analisa convergência
        print("\n=== Análise da Convergência ===")
        
        if table_a_final and table_b_final and table_c_final:
            # Verifica se todos os roteadores conhecem todas as redes
            all_networks = ['10.0.0.0/24', '10.0.1.0/24', '10.0.2.0/23']
            
            for router_name, table in [('A', table_a_final), ('B', table_b_final), ('C', table_c_final)]:
                known_networks = [net for net in all_networks if net in table]
                print(f"Roteador {router_name} conhece {len(known_networks)}/{len(all_networks)} redes: {known_networks}")
                
                if len(known_networks) == len(all_networks):
                    print(f"✅ Roteador {router_name} convergiu completamente!")
                else:
                    print(f"⚠️ Roteador {router_name} ainda não convergiu completamente")
            
            # Verifica caminhos ótimos
            print("\n=== Verificação de Caminhos Ótimos ===")
            
            # Roteador A para C deve usar B como intermediário (custo 3 vs 10)
            if '10.0.2.0/23' in table_a_final:
                route_to_c = table_a_final['10.0.2.0/23']
                if route_to_c['cost'] == 3 and route_to_c['next_hop'] == '127.0.0.1:5001':
                    print("✅ Roteador A encontrou caminho ótimo para C via B!")
                else:
                    print(f"⚠️ Roteador A não encontrou caminho ótimo para C: {route_to_c}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    finally:
        # Para todos os processos
        print("\nParando roteadores...")
        for name, process in processes:
            process.terminate()
            process.wait()
            print(f"Roteador {name} parado.")

if __name__ == '__main__':
    test_complete_example()
