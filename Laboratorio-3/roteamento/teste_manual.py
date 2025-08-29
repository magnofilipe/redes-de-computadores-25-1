#!/usr/bin/env python3

import subprocess
import time
import requests
import json

def test_manual_communication():
    print("=== Teste de Comunicação Manual ===")
    
    # Inicia apenas o roteador A
    print("Iniciando Roteador A...")
    process_a = subprocess.Popen([
        'python', 'roteador.py', 
        '-p', '5000', 
        '-f', 'exemplo/config_A.csv', 
        '--network', '10.0.0.0/24',
        '--interval', '10'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    try:
        # Verifica tabela inicial do A
        print("Tabela inicial do Roteador A:")
        response = requests.get('http://localhost:5000/routes', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data['routing_table'], indent=2))
        
        # Simula envio de tabela do B para A
        print("\nSimulando envio da tabela do B para A...")
        update_data = {
            "sender_address": "127.0.0.1:5001",
            "routing_table": {
                "10.0.1.0/24": {"cost": 0, "next_hop": "10.0.1.0/24"},
                "127.0.0.1:5002": {"cost": 2, "next_hop": "127.0.0.1:5002"}
            }
        }
        
        response = requests.post(
            'http://localhost:5000/receive_update',
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Atualização do B recebida por A!")
            
            # Verifica tabela atualizada
            response = requests.get('http://localhost:5000/routes', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("Tabela do A após receber atualização do B:")
                print(json.dumps(data['routing_table'], indent=2))
        
        # Simula envio da tabela do C para A
        print("\nSimulando envio da tabela do C para A...")
        update_data = {
            "sender_address": "127.0.0.1:5002",
            "routing_table": {
                "10.0.2.0/23": {"cost": 0, "next_hop": "10.0.2.0/23"}
            }
        }
        
        response = requests.post(
            'http://localhost:5000/receive_update',
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Atualização do C recebida por A!")
            
            # Verifica tabela final
            response = requests.get('http://localhost:5000/routes', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("Tabela final do A:")
                print(json.dumps(data['routing_table'], indent=2))
                
                # Verifica se A conhece todas as redes
                networks = ['10.0.0.0/24', '10.0.1.0/24', '10.0.2.0/23']
                known_networks = [net for net in networks if net in data['routing_table']]
                print(f"\nRedes conhecidas por A: {known_networks}")
                print(f"Total: {len(known_networks)}/{len(networks)}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        process_a.terminate()
        process_a.wait()
        print("Roteador A parado.")

if __name__ == '__main__':
    test_manual_communication()
