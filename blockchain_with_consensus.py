#!/usr/bin/env python3
"""
Blockchain con Consenso Distribuido Integrado
=============================================
Versión simplificada que combina el blockchain original de Miguel Villegas 
con el sistema de consenso distribuido.

Autor: Miguel Villegas Nicholls
Curso: Fundamentos de Blockchain
Fecha: 24 de agosto de 2025

Características:
✅ Blockchain funcional completo
✅ Consenso distribuido integrado
✅ Minería con validación de consenso
✅ Persistencia de estado
✅ API REST para interacción
"""

import datetime
import hashlib
import time
import json
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from consensus_system import ConsensusEngine, app as consensus_app
import threading
import uvicorn

# ============================================================================
# CLASES DEL BLOCKCHAIN ORIGINAL
# ============================================================================

class Transaccion:
    """Clase para representar una transacción en el blockchain."""
    
    def __init__(self, remitente: str, destinatario: str, cantidad: float, timestamp: float = None):
        self.remitente = remitente
        self.destinatario = destinatario
        self.cantidad = cantidad
        self.timestamp = timestamp or time.time()
        self.hash = self.calcular_hash()
    
    def calcular_hash(self) -> str:
        """Calcular hash SHA-256 de la transacción."""
        datos = f"{self.remitente}{self.destinatario}{self.cantidad}{self.timestamp}"
        return hashlib.sha256(datos.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir transacción a diccionario."""
        return {
            'remitente': self.remitente,
            'destinatario': self.destinatario,
            'cantidad': self.cantidad,
            'timestamp': self.timestamp,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaccion':
        """Crear transacción desde diccionario."""
        tx = cls(data['remitente'], data['destinatario'], data['cantidad'], data['timestamp'])
        tx.hash = data['hash']
        return tx

class Bloque:
    """Clase para representar un bloque en el blockchain."""
    
    def __init__(self, indice: int, transacciones: List[Transaccion], 
                 hash_anterior: str, timestamp: float = None, consenso_data: Dict = None):
        self.indice = indice
        self.timestamp = timestamp or time.time()
        self.transacciones = transacciones
        self.hash_anterior = hash_anterior
        self.consenso_data = consenso_data or {}
        self.nonce = 0
        self.hash = self.calcular_hash()
    
    def calcular_hash(self) -> str:
        """Calcular hash SHA-256 del bloque."""
        transacciones_str = ''.join([tx.hash for tx in self.transacciones])
        consenso_str = json.dumps(self.consenso_data, sort_keys=True)
        datos = f"{self.indice}{self.timestamp}{transacciones_str}{self.hash_anterior}{consenso_str}{self.nonce}"
        return hashlib.sha256(datos.encode()).hexdigest()
    
    def minar_bloque(self, dificultad: int):
        """Minar el bloque hasta encontrar un hash que cumpla la dificultad."""
        objetivo = "0" * dificultad
        
        print(f"⛏️  Minando bloque {self.indice}...")
        inicio = time.time()
        
        while self.hash[:dificultad] != objetivo:
            self.nonce += 1
            self.hash = self.calcular_hash()
            
            # Mostrar progreso cada 100,000 intentos
            if self.nonce % 100000 == 0:
                print(f"   Intentos: {self.nonce:,}")
        
        fin = time.time()
        print(f"✅ Bloque {self.indice} minado! Hash: {self.hash}")
        print(f"⏱️  Tiempo: {fin - inicio:.2f} segundos")
        print(f"🔨 Nonce: {self.nonce:,}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir bloque a diccionario."""
        return {
            'indice': self.indice,
            'timestamp': self.timestamp,
            'transacciones': [tx.to_dict() for tx in self.transacciones],
            'hash_anterior': self.hash_anterior,
            'consenso_data': self.consenso_data,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bloque':
        """Crear bloque desde diccionario."""
        transacciones = [Transaccion.from_dict(tx) for tx in data['transacciones']]
        bloque = cls(
            data['indice'],
            transacciones,
            data['hash_anterior'],
            data['timestamp'],
            data.get('consenso_data', {})
        )
        bloque.nonce = data['nonce']
        bloque.hash = data['hash']
        return bloque

class BlockchainConsenso:
    """Blockchain con consenso distribuido integrado."""
    
    def __init__(self, dificultad: int = 2):
        self.cadena: List[Bloque] = []
        self.dificultad = dificultad
        self.transacciones_pendientes: List[Transaccion] = []
        self.recompensa_mineria = 10
        self.consensus_engine = ConsensusEngine()
        
        # Crear bloque génesis
        self.crear_bloque_genesis()
        
        # Cargar estado si existe
        self.cargar_blockchain()
    
    def crear_bloque_genesis(self):
        """Crear el primer bloque de la cadena."""
        bloque_genesis = Bloque(0, [], "0", consenso_data={
            "tipo": "genesis",
            "creador": "Miguel Villegas Nicholls",
            "curso": "Fundamentos de Blockchain"
        })
        bloque_genesis.minar_bloque(self.dificultad)
        self.cadena.append(bloque_genesis)
    
    def obtener_ultimo_bloque(self) -> Bloque:
        """Obtener el último bloque de la cadena."""
        return self.cadena[-1]
    
    def crear_transaccion(self, remitente: str, destinatario: str, cantidad: float):
        """Crear nueva transacción pendiente."""
        transaccion = Transaccion(remitente, destinatario, cantidad)
        self.transacciones_pendientes.append(transaccion)
        print(f"💰 Transacción creada: {remitente} → {destinatario} ({cantidad})")
        return transaccion
    
    def minar_con_consenso(self, direccion_minero: str) -> Optional[Bloque]:
        """Minar nuevo bloque con validación de consenso."""
        if not self.transacciones_pendientes:
            print("⚠️  No hay transacciones pendientes para minar")
            return None
        
        print("\n🔗 Iniciando minería con consenso distribuido...")
        
        # 1. Verificar estado del consenso
        try:
            result = self.consensus_engine.get_consensus_result()
            print(f"📊 Estado del consenso: {result.agreementPercentage}% de acuerdo")
            
            if result.hasAgreement:
                print("✅ Consenso alcanzado, procediendo con la minería")
                consenso_info = {
                    "consenso_alcanzado": True,
                    "porcentaje_acuerdo": result.agreementPercentage,
                    "votos_totales": result.totalVotes,
                    "acuerdo": result.agreement
                }
            else:
                print("⚠️  Consenso no alcanzado, minando con datos parciales")
                consenso_info = {
                    "consenso_alcanzado": False,
                    "porcentaje_acuerdo": result.agreementPercentage,
                    "votos_totales": result.totalVotes,
                    "nodos_registrados": len(self.consensus_engine.state.registry.nodes)
                }
        
        except Exception as e:
            print(f"⚠️  Error verificando consenso: {e}")
            consenso_info = {"error": "Consenso no disponible"}
        
        # 2. Agregar recompensa de minería
        recompensa = Transaccion("Sistema", direccion_minero, self.recompensa_mineria)
        transacciones = self.transacciones_pendientes + [recompensa]
        
        # 3. Crear nuevo bloque con información de consenso
        nuevo_bloque = Bloque(
            len(self.cadena),
            transacciones,
            self.obtener_ultimo_bloque().hash,
            consenso_data=consenso_info
        )
        
        # 4. Minar el bloque
        nuevo_bloque.minar_bloque(self.dificultad)
        
        # 5. Agregar a la cadena
        self.cadena.append(nuevo_bloque)
        
        # 6. Limpiar transacciones pendientes
        self.transacciones_pendientes = []
        
        # 7. Guardar estado
        self.guardar_blockchain()
        
        print(f"🎉 Bloque {nuevo_bloque.indice} minado y agregado a la cadena!")
        return nuevo_bloque
    
    def es_cadena_valida(self) -> bool:
        """Validar integridad de la cadena completa."""
        for i in range(1, len(self.cadena)):
            bloque_actual = self.cadena[i]
            bloque_anterior = self.cadena[i-1]
            
            # Verificar hash del bloque actual
            if bloque_actual.hash != bloque_actual.calcular_hash():
                print(f"❌ Hash inválido en bloque {i}")
                return False
            
            # Verificar enlace con bloque anterior
            if bloque_actual.hash_anterior != bloque_anterior.hash:
                print(f"❌ Enlace roto en bloque {i}")
                return False
        
        return True
    
    def obtener_balance(self, direccion: str) -> float:
        """Obtener balance de una dirección."""
        balance = 0.0
        
        for bloque in self.cadena:
            for transaccion in bloque.transacciones:
                if transaccion.remitente == direccion:
                    balance -= transaccion.cantidad
                if transaccion.destinatario == direccion:
                    balance += transaccion.cantidad
        
        # Considerar transacciones pendientes
        for transaccion in self.transacciones_pendientes:
            if transaccion.remitente == direccion:
                balance -= transaccion.cantidad
        
        return balance
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas completas del blockchain."""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS BLOCKCHAIN + CONSENSO")
        print("="*60)
        print(f"🔗 Bloques en la cadena: {len(self.cadena)}")
        print(f"📋 Transacciones pendientes: {len(self.transacciones_pendientes)}")
        print(f"💰 Recompensa por bloque: {self.recompensa_mineria}")
        print(f"⚡ Dificultad de minería: {self.dificultad}")
        
        # Estadísticas de consenso
        try:
            nodes = len(self.consensus_engine.state.registry.nodes)
            turn = self.consensus_engine.state.turn_state.current_turn
            votes = len(self.consensus_engine.state.turn_state.votes)
            tokens = sum(self.consensus_engine.state.tokens.frozen_tokens.values())
            
            print(f"🌐 Nodos en consenso: {nodes}")
            print(f"🔄 Turno actual: {turn}")
            print(f"🗳️ Votos activos: {votes}")
            print(f"🪙 Tokens congelados: {tokens}")
        except:
            print("⚠️ Estadísticas de consenso no disponibles")
        
        print("="*60)
        
        # Validar cadena
        if self.es_cadena_valida():
            print("✅ Blockchain válido")
        else:
            print("❌ Blockchain inválido!")
    
    def guardar_blockchain(self):
        """Guardar blockchain a archivo JSON."""
        try:
            datos = {
                'cadena': [bloque.to_dict() for bloque in self.cadena],
                'transacciones_pendientes': [tx.to_dict() for tx in self.transacciones_pendientes],
                'dificultad': self.dificultad,
                'recompensa_mineria': self.recompensa_mineria,
                'timestamp': time.time()
            }
            
            with open('blockchain_estado.json', 'w') as f:
                json.dump(datos, f, indent=2)
            
            print("💾 Blockchain guardado exitosamente")
            
        except Exception as e:
            print(f"❌ Error guardando blockchain: {e}")
    
    def cargar_blockchain(self):
        """Cargar blockchain desde archivo JSON."""
        try:
            with open('blockchain_estado.json', 'r') as f:
                datos = json.load(f)
            
            # Cargar cadena
            self.cadena = [Bloque.from_dict(bloque) for bloque in datos['cadena']]
            
            # Cargar transacciones pendientes
            self.transacciones_pendientes = [
                Transaccion.from_dict(tx) for tx in datos['transacciones_pendientes']
            ]
            
            # Cargar configuración
            self.dificultad = datos.get('dificultad', 2)
            self.recompensa_mineria = datos.get('recompensa_mineria', 10)
            
            print("📂 Blockchain cargado exitosamente")
            
        except FileNotFoundError:
            print("📝 No se encontró estado previo, iniciando nuevo blockchain")
        except Exception as e:
            print(f"❌ Error cargando blockchain: {e}")

# ============================================================================
# INTEGRACIÓN CON SERVIDOR DE CONSENSO
# ============================================================================

class BlockchainConsensusServer:
    """Servidor que combina blockchain y consenso."""
    
    def __init__(self):
        self.blockchain = BlockchainConsenso()
        self.server_thread = None
    
    def start_consensus_server(self):
        """Iniciar servidor de consenso en hilo separado."""
        def run_server():
            uvicorn.run(consensus_app, host="0.0.0.0", port=8000, log_level="warning")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        time.sleep(2)  # Esperar a que inicie
        print("🌐 Servidor de consenso iniciado en http://localhost:8000")
    
    def demo_completa(self):
        """Demostración completa del sistema."""
        print("🎓 Demostración Blockchain + Consenso Distribuido")
        print("=" * 60)
        
        # 1. Iniciar servidor
        self.start_consensus_server()
        
        # 2. Registrar algunos nodos de prueba
        self.registrar_nodos_demo()
        
        # 3. Crear transacciones de prueba
        self.crear_transacciones_demo()
        
        # 4. Minar con consenso
        bloque = self.blockchain.minar_con_consenso("Miguel")
        
        # 5. Mostrar estadísticas
        self.blockchain.mostrar_estadisticas()
        
        return bloque
    
    def registrar_nodos_demo(self):
        """Registrar nodos de demostración."""
        nodos_demo = [
            {"nodeId": "node_1", "ip": "192.168.1.10"},
            {"nodeId": "node_2", "ip": "192.168.1.20"},
            {"nodeId": "node_3", "ip": "192.168.1.30"},
        ]
        
        for nodo in nodos_demo:
            try:
                self.blockchain.consensus_engine.register_node(
                    nodo["nodeId"], 
                    nodo["ip"], 
                    f"pubkey_{nodo['nodeId']}"
                )
                print(f"📝 Nodo registrado: {nodo['nodeId']} ({nodo['ip']})")
            except Exception as e:
                print(f"⚠️ Error registrando {nodo['nodeId']}: {e}")
    
    def crear_transacciones_demo(self):
        """Crear transacciones de demostración."""
        transacciones_demo = [
            ("Alice", "Bob", 50.0),
            ("Bob", "Charlie", 25.0),
            ("Charlie", "Alice", 10.0),
        ]
        
        for remitente, destinatario, cantidad in transacciones_demo:
            self.blockchain.crear_transaccion(remitente, destinatario, cantidad)

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal del sistema integrado."""
    print("🎓 Blockchain con Consenso Distribuido - Miguel Villegas Nicholls")
    print("=" * 70)
    
    server = BlockchainConsensusServer()
    
    while True:
        print("\n🔧 OPCIONES:")
        print("1. Demostración completa")
        print("2. Crear transacción")
        print("3. Minar bloque")
        print("4. Ver estadísticas")
        print("5. Validar blockchain")
        print("6. Ver balance")
        print("7. Iniciar servidor consenso")
        print("0. Salir")
        
        try:
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == "1":
                server.demo_completa()
            
            elif opcion == "2":
                remitente = input("Remitente: ")
                destinatario = input("Destinatario: ")
                cantidad = float(input("Cantidad: "))
                server.blockchain.crear_transaccion(remitente, destinatario, cantidad)
            
            elif opcion == "3":
                minero = input("Dirección del minero: ")
                server.blockchain.minar_con_consenso(minero)
            
            elif opcion == "4":
                server.blockchain.mostrar_estadisticas()
            
            elif opcion == "5":
                if server.blockchain.es_cadena_valida():
                    print("✅ Blockchain válido")
                else:
                    print("❌ Blockchain inválido")
            
            elif opcion == "6":
                direccion = input("Dirección: ")
                balance = server.blockchain.obtener_balance(direccion)
                print(f"💰 Balance de {direccion}: {balance}")
            
            elif opcion == "7":
                server.start_consensus_server()
            
            elif opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
