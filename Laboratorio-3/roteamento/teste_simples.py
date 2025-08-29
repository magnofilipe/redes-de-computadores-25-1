#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import requests
import json

def test_router():
    """Testa se o roteador está funcionando corretamente"""
    
    print("=== Teste do Roteador ===")
    
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
        # Testa se o roteador está respondendo
        print("Testando endpoint /routes...")
        response = requests.get('http://localhost:5000/routes', timeout=5)
        
        if response.status_code == 200:
            print("✅ Roteador está funcionando!")
            data = response.json()
            print("Tabela de roteamento inicial:")
            print(json.dumps(data['routing_table'], indent=2))
            
            # Testa envio de atualização
            print("\nTestando envio de atualização...")
            update_data = {
                "sender_address": "127.0.0.1:5001",
                "routing_table": {
                    "10.0.1.0/24": {"cost": 0, "next_hop": "10.0.1.0/24"},
                    "10.0.2.0/24": {"cost": 1, "next_hop": "127.0.0.1:5001"}
                }
            }
            
            response = requests.post(
                'http://localhost:5000/receive_update',
                json=update_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Atualização recebida com sucesso!")
                
                # Verifica se a tabela foi atualizada
                response = requests.get('http://localhost:5000/routes', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print("Tabela de roteamento após atualização:")
                    print(json.dumps(data['routing_table'], indent=2))
            else:
                print(f"❌ Erro ao enviar atualização: {response.status_code}")
                
        else:
            print(f"❌ Roteador não está respondendo: {response.status_code}")
            
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
    test_router()
