#!/usr/bin/env python3
"""
Script de prueba para el protocolo de consenso.
Demuestra el flujo completo de consenso.
"""

import sys
import os
import requests
import json
import base64
import time

# Configuración
BASE_URL = "http://localhost:8000"
NODES = [
    {"nodeId": "miguel@node1.com", "ip": "192.168.1.10"},
    {"nodeId": "alice@node2.com", "ip": "192.168.1.20"}, 
    {"nodeId": "bob@node3.com", "ip": "192.168.1.30"}
]


def create_mock_signature(data: str) -> str:
    """Crea una firma mock para las pruebas."""
    # En una implementación real, esto usaría GPG
    # Para pruebas, creamos una firma determinística
    import hashlib
    
    signature_data = f"MOCK_SIGNATURE:{data}"
    signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
    
    mock_signature = f"""-----BEGIN PGP SIGNATURE-----

{signature_hash[:64]}
{signature_hash[64:]}
-----END PGP SIGNATURE-----"""
    
    return base64.b64encode(mock_signature.encode()).decode()


def test_server_status():
    """Verifica que el servidor esté ejecutándose."""
    print("🔍 Verificando estado del servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor activo")
            print(f"   Estado: {response.json()}")
            return True
        else:
            print(f"❌ Servidor responde con error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print(f"   Asegúrate de que el servidor esté ejecutándose en {BASE_URL}")
        return False


def test_node_registration():
    """Prueba el registro de nodos."""
    print("\n📝 Registrando nodos...")
    
    registered_nodes = []
    
    for node in NODES:
        print(f"   Registrando {node['nodeId']}...")
        
        # Crear payload
        payload = {
            "nodeId": node['nodeId'],
            "ip": node['ip'],
            "publicKey": f"MOCK_PUBLIC_KEY_{node['nodeId']}"
        }
        
        # Crear firma mock
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        signature = create_mock_signature(payload_json)
        
        # Agregar firma al payload
        payload["signature"] = signature
        
        try:
            response = requests.post(f"{BASE_URL}/network/register", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {node['nodeId']} registrado (orden: {result['assignedOrder']})")
                registered_nodes.append({**node, **result})
            else:
                print(f"   ❌ Error registrando {node['nodeId']}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")
    
    return registered_nodes


def test_token_freezing():
    """Prueba la congelación de tokens."""
    print("\n🧊 Congelando tokens...")
    
    tokens_to_freeze = [100, 200, 150]  # Tokens por nodo
    
    for i, node in enumerate(NODES):
        tokens = tokens_to_freeze[i]
        print(f"   Congelando {tokens} tokens para {node['nodeId']}...")
        
        payload = {
            "nodeId": node['nodeId'],
            "tokens": tokens
        }
        
        # Crear firma
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        signature = create_mock_signature(payload_json)
        payload["signature"] = signature
        
        try:
            response = requests.post(f"{BASE_URL}/tokens/freeze", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {tokens} tokens congelados para {node['nodeId']}")
            else:
                print(f"   ❌ Error congelando tokens: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")


def test_seed_generation():
    """Prueba la generación del seed por el líder."""
    print("\n🎲 Generando seed del líder...")
    
    # El líder del turno 0 será el primer nodo (IP más alta determina orden)
    leader = NODES[0]  # Simplificado para la demo
    turn = 0
    
    print(f"   Líder del turno {turn}: {leader['nodeId']}")
    
    # Crear seed mock
    import random
    seed_value = random.randint(0, 0xFFFFFFFF)
    encrypted_seed = base64.b64encode(seed_value.to_bytes(4, 'little')).decode()
    
    payload = {
        "leaderId": leader['nodeId'],
        "encryptedSeed": encrypted_seed,
        "turn": turn
    }
    
    # Crear firma
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    signature = create_mock_signature(payload_json)
    payload["signature"] = signature
    
    try:
        response = requests.post(f"{BASE_URL}/leader/random-seed", json=payload)
        
        if response.status_code == 200:
            print(f"   ✅ Seed enviado por {leader['nodeId']}")
            return True
        else:
            print(f"   ❌ Error enviando seed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        return False


def test_voting():
    """Prueba el proceso de votación."""
    print("\n🗳️  Enviando votos...")
    
    for node in NODES:
        print(f"   Votando desde {node['nodeId']}...")
        
        # Crear voto mock (índice del nodo seleccionado)
        selected_index = 1  # Todos votan por el nodo índice 1 para la demo
        encrypted_vote = base64.b64encode(selected_index.to_bytes(4, 'little')).decode()
        
        payload = {
            "nodeId": node['nodeId'],
            "encryptedVote": encrypted_vote
        }
        
        # Crear firma
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        signature = create_mock_signature(payload_json)
        payload["signature"] = signature
        
        try:
            response = requests.post(f"{BASE_URL}/consensus/vote", json=payload)
            
            if response.status_code == 200:
                print(f"   ✅ Voto registrado desde {node['nodeId']}")
            else:
                print(f"   ❌ Error enviando voto: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")


def test_consensus_result():
    """Prueba la obtención del resultado del consenso."""
    print("\n📊 Obteniendo resultado del consenso...")
    
    try:
        response = requests.get(f"{BASE_URL}/consensus/result")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Líder seleccionado: {result['leader']}")
            print(f"   Porcentaje de acuerdo: {result['agreement']:.2%}")
            print(f"   Umbral 2/3 alcanzado: {'✅' if result['thresholdReached'] else '❌'}")
            return result
        else:
            print(f"   ❌ Error obteniendo resultado: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        return None


def main():
    """Ejecuta todas las pruebas en secuencia."""
    print("🧪 PRUEBAS DEL PROTOCOLO DE CONSENSO")
    print("=" * 50)
    
    # Verificar servidor
    if not test_server_status():
        print("\n❌ No se puede continuar sin el servidor activo.")
        print("   Ejecuta: python run_consensus.py")
        return
    
    # Cambiar a proveedor mock para las pruebas
    print("\n🔧 Configurando proveedor criptográfico mock...")
    try:
        requests.post(f"{BASE_URL}/debug/set-mock-provider")
    except:
        pass  # Endpoint no implementado, pero no es crítico
    
    # Ejecutar pruebas
    registered_nodes = test_node_registration()
    
    if len(registered_nodes) > 0:
        test_token_freezing()
        
        if test_seed_generation():
            time.sleep(1)  # Dar tiempo para procesar
            test_voting()
            time.sleep(1)
            result = test_consensus_result()
            
            if result and result['thresholdReached']:
                print("\n✅ ¡Consenso alcanzado exitosamente!")
                print(f"   El nodo '{result['leader']}' puede proceder a validar bloques")
            else:
                print("\n⚠️  Consenso no alcanzado o resultado inválido")
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")
    
    # Mostrar información adicional
    print(f"\n📖 Documentación de la API: {BASE_URL}/docs")
    print(f"🔍 Estado actual: {BASE_URL}/status")
    print(f"👥 Nodos registrados: {BASE_URL}/debug/nodes")
    print(f"🗳️  Votos actuales: {BASE_URL}/debug/votes")


if __name__ == "__main__":
    main()
