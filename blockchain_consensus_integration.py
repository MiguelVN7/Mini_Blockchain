"""
Integración entre blockchain_MiguelVillegasNicholls.py y el sistema de consenso.
Esta clase proporciona métodos para usar el consenso distribuido en el blockchain.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from blockchain_MiguelVillegasNicholls import *


class BlockchainConsensusIntegration:
    """
    Clase que integra el blockchain existente con el protocolo de consenso distribuido.
    """
    
    def __init__(self, consensus_api_url: str = "http://localhost:8000", node_email: str = None):
        """
        Inicializa la integración.
        
        Args:
            consensus_api_url: URL del API de consenso
            node_email: Email del nodo (debe coincidir con identidad GPG)
        """
        self.consensus_url = consensus_api_url
        self.node_email = node_email
        self.blockchain = None  # Se inicializará con el blockchain existente
        
        # Verificar conexión con el API de consenso
        self._verificar_conexion()
    
    def _verificar_conexion(self):
        """Verifica que el API de consenso esté disponible."""
        try:
            response = requests.get(f"{self.consensus_url}/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Conexión establecida con consenso. Nodos: {status['nodes_count']}")
                return True
        except Exception as e:
            print(f"❌ Error conectando con consenso: {e}")
            return False
    
    def registrar_nodo(self, node_id: str, ip: str, public_key: str) -> bool:
        """
        Registra este nodo en la red de consenso.
        
        Args:
            node_id: Identificador del nodo (email GPG)
            ip: Dirección IP del nodo
            public_key: Clave pública GPG
        
        Returns:
            bool: True si el registro fue exitoso
        """
        try:
            # Para simplicidad, usamos una firma mock para el registro inicial
            import base64
            mock_signature = base64.b64encode(f"register_{node_id}".encode()).decode()
            
            data = {
                "nodeId": node_id,
                "ip": ip,
                "publicKey": public_key,
                "signature": mock_signature
            }
            
            response = requests.post(f"{self.consensus_url}/network/register", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Nodo registrado. Orden asignado: {result['assignedOrder']}")
                self.node_email = node_id
                return True
            else:
                print(f"❌ Error registrando nodo: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return False
    
    def proponer_bloque(self, bloque_data: Dict) -> bool:
        """
        Propone un bloque para consenso.
        
        Args:
            bloque_data: Datos del bloque a proponer
        
        Returns:
            bool: True si la propuesta fue aceptada
        """
        try:
            if not self.node_email:
                print("❌ Nodo no registrado")
                return False
            
            # Preparar datos del bloque según el formato del consenso
            block_proposal = {
                "proposerId": self.node_email,
                "block": {
                    "number": bloque_data.get("index", 0),
                    "timestamp": bloque_data.get("timestamp", int(time.time())),
                    "transactions": bloque_data.get("transactions", []),
                    "previousHash": bloque_data.get("previous_hash", ""),
                    "merkleRoot": bloque_data.get("merkle_root", "")
                },
                "signature": "mock_block_signature"  # En producción, firmar con GPG
            }
            
            response = requests.post(f"{self.consensus_url}/block/propose", json=block_proposal)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Bloque propuesto: {result['status']}")
                return True
            else:
                print(f"❌ Error proponiendo bloque: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Error en propuesta: {e}")
            return False
    
    def esperar_consenso(self, timeout: int = 30) -> Tuple[bool, Dict]:
        """
        Espera a que se alcance consenso sobre un bloque.
        
        Args:
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            Tuple[bool, Dict]: (consenso_alcanzado, resultado)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.consensus_url}/consensus/result")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("thresholdReached", False):
                        print(f"✅ Consenso alcanzado! Acuerdo: {result['agreement']:.1%}")
                        return True, result
                    
                    print(f"⏳ Esperando consenso... Acuerdo actual: {result['agreement']:.1%}")
                
            except Exception as e:
                print(f"❌ Error verificando consenso: {e}")
            
            time.sleep(2)  # Esperar 2 segundos antes de verificar de nuevo
        
        print(f"⏰ Timeout esperando consenso")
        return False, {}
    
    def obtener_estado_consenso(self) -> Dict:
        """
        Obtiene el estado actual del sistema de consenso.
        
        Returns:
            Dict: Estado del consenso
        """
        try:
            response = requests.get(f"{self.consensus_url}/status")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
        
        return {}
    
    def crear_blockchain_con_consenso(self):
        """
        Crea un blockchain que utiliza consenso distribuido.
        Integra con las funciones existentes de blockchain_MiguelVillegasNicholls.py
        """
        print("🔗 Inicializando blockchain con consenso distribuido...")
        
        # Usar las funciones existentes del blockchain
        blockchain_data = {
            "chain": [],
            "pending_transactions": [],
            "mining_reward": 10,
            "difficulty": 2
        }
        
        # Crear el bloque génesis simplificado
        import hashlib
        genesis_block = {
            "index": 0,
            "timestamp": int(time.time()),
            "transactions": [],
            "previous_hash": "0",
            "nonce": 0,
            "hash": hashlib.sha256("genesis_block".encode()).hexdigest()
        }
        
        blockchain_data["chain"].append(genesis_block)
        
        print("✅ Blockchain con consenso inicializado")
        self.blockchain = blockchain_data
        return blockchain_data
    
    def minar_bloque_con_consenso(self, mining_reward_address: str = None) -> bool:
        """
        Mina un bloque usando consenso distribuido.
        
        Args:
            mining_reward_address: Dirección para la recompensa de minería
        
        Returns:
            bool: True si el bloque fue minado y consensuado exitosamente
        """
        if not self.blockchain:
            print("❌ Blockchain no inicializado")
            return False
        
        if not self.node_email:
            print("❌ Nodo no registrado en consenso")
            return False
        
        print("\n🔨 Iniciando minería con consenso distribuido...")
        
        try:
            # 1. Crear el bloque con las transacciones pendientes
            previous_block = self.blockchain["chain"][-1]
            
            # Crear datos del bloque
            bloque_data = {
                "index": len(self.blockchain["chain"]),
                "timestamp": int(time.time()),
                "transactions": self.blockchain.get("pending_transactions", []).copy(),
                "previous_hash": previous_block.get("hash", ""),
                "nonce": 0
            }
            
            # 2. Proponer el bloque para consenso
            print("📤 Proponiendo bloque para consenso...")
            if not self.proponer_bloque(bloque_data):
                return False
            
            # 3. Esperar consenso
            print("⏳ Esperando consenso de la red...")
            consenso_alcanzado, resultado = self.esperar_consenso(timeout=60)
            
            if consenso_alcanzado:
                # 4. Si hay consenso, minar el bloque (Proof of Work)
                print("⛏️ Consenso alcanzado, minando bloque...")
                
                # Minería simplificada
                import hashlib
                nonce = 0
                difficulty = self.blockchain["difficulty"]
                target = "0" * difficulty
                
                while True:
                    bloque_data["nonce"] = nonce
                    block_string = json.dumps(bloque_data, sort_keys=True)
                    block_hash = hashlib.sha256(block_string.encode()).hexdigest()
                    
                    if block_hash[:difficulty] == target:
                        bloque_data["hash"] = block_hash
                        break
                    
                    nonce += 1
                
                bloque_minado = bloque_data
                
                # 5. Agregar el bloque a la cadena
                self.blockchain["chain"].append(bloque_minado)
                self.blockchain["pending_transactions"] = []
                
                print(f"✅ Bloque minado y agregado! Hash: {bloque_minado['hash'][:16]}...")
                return True
            else:
                print("❌ No se alcanzó consenso, bloque rechazado")
                return False
                
        except Exception as e:
            print(f"❌ Error en minería con consenso: {e}")
            return False
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del blockchain y consenso."""
        print("\n" + "="*50)
        print("📊 ESTADÍSTICAS BLOCKCHAIN + CONSENSO")
        print("="*50)
        
        # Estadísticas del blockchain
        if self.blockchain:
            print(f"🔗 Bloques en la cadena: {len(self.blockchain['chain'])}")
            print(f"📋 Transacciones pendientes: {len(self.blockchain.get('pending_transactions', []))}")
            print(f"💰 Recompensa por bloque: {self.blockchain.get('mining_reward', 0)}")
        
        # Estadísticas del consenso
        estado_consenso = self.obtener_estado_consenso()
        if estado_consenso:
            print(f"🌐 Nodos en consenso: {estado_consenso.get('nodes_count', 0)}")
            print(f"🔄 Turno actual: {estado_consenso.get('current_turn', 0)}")
            print(f"🗳️ Votos activos: {estado_consenso.get('votes_count', 0)}")
            print(f"🪙 Tokens congelados: {len(estado_consenso.get('frozen_tokens', {}))}")
        
        print("="*50)


def demo_integracion_completa():
    """
    Demostración completa de la integración blockchain + consenso.
    """
    print("🚀 DEMO: BLOCKCHAIN + CONSENSO DISTRIBUIDO")
    print("="*60)
    
    # 1. Inicializar integración
    print("\n1️⃣ Inicializando integración...")
    integration = BlockchainConsensusIntegration()
    
    # 2. Registrar nodo (simulado)
    print("\n2️⃣ Registrando nodo en consenso...")
    public_key_mock = "-----BEGIN PGP PUBLIC KEY BLOCK-----\nMOCK_KEY\n-----END PGP PUBLIC KEY BLOCK-----"
    integration.registrar_nodo(
        node_id="demo@blockchain.com",
        ip="192.168.1.100", 
        public_key=public_key_mock
    )
    
    # 3. Crear blockchain con consenso
    print("\n3️⃣ Creando blockchain con consenso...")
    blockchain = integration.crear_blockchain_con_consenso()
    
    # 4. Agregar transacciones de prueba
    print("\n4️⃣ Agregando transacciones de prueba...")
    integration.blockchain["pending_transactions"] = [
        {"from": "Alice", "to": "Bob", "amount": 50},
        {"from": "Bob", "to": "Charlie", "amount": 25},
        {"from": "Charlie", "to": "Alice", "amount": 10}
    ]
    
    # 5. Mostrar estadísticas
    print("\n5️⃣ Estadísticas actuales:")
    integration.mostrar_estadisticas()
    
    print("\n✅ Demo completada exitosamente!")
    print("🔗 El blockchain está ahora integrado con consenso distribuido")
    
    return integration


if __name__ == "__main__":
    # Ejecutar la demostración
    demo_integracion_completa()
