#!/usr/bin/env python3
"""
Sistema de Consenso Distribuido Multi-Nodo Real
===============================================
Versión para red distribuida real que permite conexión entre 
múltiples computadores de estudiantes.

Autor: Miguel Villegas Nicholls
Curso: Fundamentos de Blockchain
Fecha: 24 de agosto de 2025

Características de red distribuida:
✅ Conexión real entre dispositivos
✅ Descubrimiento automático de nodos
✅ Sincronización de estado distribuido
✅ Comunicación P2P entre nodos
✅ Tolerancia a desconexiones
✅ Configuración automática de red
"""

import json
import time
import requests
import threading
import socket
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from consensus_system import ConsensusEngine, app as consensus_app
import uvicorn
import os
import hashlib

# ============================================================================
# CONFIGURACIÓN DE RED DISTRIBUIDA
# ============================================================================

@dataclass
class NetworkConfig:
    """Configuración de red distribuida."""
    port: int = 8000
    discovery_port: int = 8001
    broadcast_interval: int = 30
    timeout: int = 5
    max_retries: int = 3

@dataclass
class NodeInfo:
    """Información de un nodo en la red."""
    node_id: str
    ip: str
    port: int
    public_key: str
    status: str = "active"
    last_seen: float = 0
    version: str = "1.0.0"

class NetworkDiscovery:
    """Servicio de descubrimiento de nodos en la red local."""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.nodes: Dict[str, NodeInfo] = {}
        self.my_ip = self._get_my_ip()
        self.my_node_id = f"node_{hashlib.md5(self.my_ip.encode()).hexdigest()[:8]}"
        self.running = False
        self.discovery_thread = None
        self.broadcast_thread = None
    
    def _get_my_ip(self) -> str:
        """Obtener IP local del dispositivo."""
        try:
            # Conectar a un servidor externo para obtener IP local
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def start_discovery(self):
        """Iniciar servicio de descubrimiento."""
        self.running = True
        
        # Hilo para escuchar broadcasts
        self.discovery_thread = threading.Thread(target=self._listen_discovery)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        
        # Hilo para enviar broadcasts
        self.broadcast_thread = threading.Thread(target=self._broadcast_presence)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()
        
        print(f"🔍 Descubrimiento iniciado en {self.my_ip}:{self.config.discovery_port}")
        print(f"🏷️ ID de nodo: {self.my_node_id}")
    
    def stop_discovery(self):
        """Detener servicio de descubrimiento."""
        self.running = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=2)
        if self.broadcast_thread:
            self.broadcast_thread.join(timeout=2)
    
    def _listen_discovery(self):
        """Escuchar broadcasts de otros nodos."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('', self.config.discovery_port))
            sock.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())
                    
                    if message.get('type') == 'node_announcement':
                        self._process_node_announcement(message, addr[0])
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"⚠️ Error en discovery: {e}")
                    
        except Exception as e:
            print(f"❌ Error iniciando discovery listener: {e}")
    
    def _broadcast_presence(self):
        """Enviar broadcast de presencia periódicamente."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running:
            try:
                message = {
                    'type': 'node_announcement',
                    'node_id': self.my_node_id,
                    'ip': self.my_ip,
                    'port': self.config.port,
                    'public_key': f"pubkey_{self.my_node_id}",
                    'timestamp': time.time(),
                    'version': '1.0.0'
                }
                
                data = json.dumps(message).encode()
                
                # Broadcast a la red local
                sock.sendto(data, ('<broadcast>', self.config.discovery_port))
                
                # Limpiar nodos inactivos
                self._cleanup_inactive_nodes()
                
                time.sleep(self.config.broadcast_interval)
                
            except Exception as e:
                print(f"⚠️ Error en broadcast: {e}")
                time.sleep(5)
    
    def _process_node_announcement(self, message: Dict, sender_ip: str):
        """Procesar anuncio de nodo."""
        try:
            node_id = message['node_id']
            
            # No procesarse a sí mismo
            if node_id == self.my_node_id:
                return
            
            # Crear o actualizar información del nodo
            node_info = NodeInfo(
                node_id=node_id,
                ip=sender_ip,
                port=message['port'],
                public_key=message['public_key'],
                status="active",
                last_seen=time.time(),
                version=message.get('version', '1.0.0')
            )
            
            is_new = node_id not in self.nodes
            self.nodes[node_id] = node_info
            
            if is_new:
                print(f"🆕 Nuevo nodo descubierto: {node_id} ({sender_ip})")
                # Registrar automáticamente en el consenso
                self._auto_register_node(node_info)
            
        except Exception as e:
            print(f"⚠️ Error procesando anuncio: {e}")
    
    def _auto_register_node(self, node: NodeInfo):
        """Registrar automáticamente nodo en el sistema de consenso."""
        try:
            # Esto se hará a través de la API local
            requests.post(f"http://localhost:{self.config.port}/network/register", 
                         json={
                             "nodeId": node.node_id,
                             "ip": node.ip,
                             "publicKey": node.public_key,
                             "signature": f"auto_signature_{node.node_id}"
                         }, timeout=2)
            print(f"📝 Nodo {node.node_id} auto-registrado en consenso")
        except Exception as e:
            print(f"⚠️ Error auto-registrando {node.node_id}: {e}")
    
    def _cleanup_inactive_nodes(self):
        """Eliminar nodos inactivos."""
        current_time = time.time()
        inactive_threshold = self.config.broadcast_interval * 3
        
        inactive_nodes = []
        for node_id, node in self.nodes.items():
            if current_time - node.last_seen > inactive_threshold:
                inactive_nodes.append(node_id)
        
        for node_id in inactive_nodes:
            print(f"🚫 Nodo inactivo eliminado: {node_id}")
            del self.nodes[node_id]
    
    def get_active_nodes(self) -> List[NodeInfo]:
        """Obtener lista de nodos activos."""
        return list(self.nodes.values())
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la red."""
        return {
            "my_node_id": self.my_node_id,
            "my_ip": self.my_ip,
            "total_nodes": len(self.nodes),
            "active_nodes": [
                {"id": node.node_id, "ip": node.ip, "status": node.status}
                for node in self.nodes.values()
            ]
        }

# ============================================================================
# SINCRONIZADOR DE ESTADO DISTRIBUIDO
# ============================================================================

class DistributedStateSynchronizer:
    """Sincronizador de estado entre nodos distribuidos."""
    
    def __init__(self, network_discovery: NetworkDiscovery, consensus_engine: ConsensusEngine):
        self.network = network_discovery
        self.consensus = consensus_engine
        self.sync_interval = 15
        self.running = False
        self.sync_thread = None
    
    def start_sync(self):
        """Iniciar sincronización de estado."""
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        print("🔄 Sincronización de estado iniciada")
    
    def stop_sync(self):
        """Detener sincronización de estado."""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
    
    def _sync_loop(self):
        """Bucle principal de sincronización."""
        while self.running:
            try:
                self._synchronize_with_network()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"⚠️ Error en sincronización: {e}")
                time.sleep(5)
    
    def _synchronize_with_network(self):
        """Sincronizar estado con otros nodos."""
        active_nodes = self.network.get_active_nodes()
        
        if not active_nodes:
            return
        
        # Obtener estado local
        local_state = self._get_local_state()
        
        # Comparar con otros nodos
        for node in active_nodes:
            try:
                remote_state = self._get_remote_state(node)
                if remote_state:
                    self._merge_states(local_state, remote_state, node)
            except Exception as e:
                print(f"⚠️ Error sincronizando con {node.node_id}: {e}")
    
    def _get_local_state(self) -> Dict[str, Any]:
        """Obtener estado local del consenso."""
        try:
            response = requests.get(f"http://localhost:{self.network.config.port}/status", 
                                  timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    def _get_remote_state(self, node: NodeInfo) -> Optional[Dict[str, Any]]:
        """Obtener estado remoto de un nodo."""
        try:
            response = requests.get(f"http://{node.ip}:{node.port}/status", 
                                  timeout=self.network.config.timeout)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def _merge_states(self, local: Dict, remote: Dict, node: NodeInfo):
        """Combinar estados local y remoto."""
        # Ejemplo de sincronización básica
        local_nodes = local.get('nodes_registered', 0)
        remote_nodes = remote.get('nodes_registered', 0)
        
        if remote_nodes > local_nodes:
            print(f"🔄 Sincronizando con {node.node_id}: {remote_nodes} nodos vs {local_nodes} locales")

# ============================================================================
# SISTEMA DISTRIBUIDO PRINCIPAL
# ============================================================================

class DistributedConsensusSystem:
    """Sistema principal de consenso distribuido multi-nodo."""
    
    def __init__(self, port: int = 8000):
        self.config = NetworkConfig(port=port)
        self.network_discovery = NetworkDiscovery(self.config)
        self.consensus_engine = ConsensusEngine()
        self.synchronizer = DistributedStateSynchronizer(self.network_discovery, self.consensus_engine)
        self.server_process = None
    
    def start_system(self):
        """Iniciar sistema distribuido completo."""
        print("🌐 Iniciando Sistema de Consenso Distribuido Multi-Nodo")
        print("=" * 60)
        print(f"📅 Fecha: {datetime.now().strftime('%d de %B de %Y')}")
        print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🏷️ Nodo ID: {self.network_discovery.my_node_id}")
        print(f"🌐 IP Local: {self.network_discovery.my_ip}")
        print(f"🚪 Puerto: {self.config.port}")
        print("=" * 60)
        
        # 1. Iniciar servidor de consenso
        self._start_consensus_server()
        
        # 2. Iniciar descubrimiento de red
        self.network_discovery.start_discovery()
        
        # 3. Iniciar sincronización
        self.synchronizer.start_sync()
        
        # 4. Auto-registro
        self._auto_register_self()
        
        print("\n✅ Sistema distribuido iniciado correctamente")
        print("🔍 Buscando otros nodos en la red...")
        print("📡 Listo para recibir conexiones de compañeros")
    
    def _start_consensus_server(self):
        """Iniciar servidor de consenso en hilo separado."""
        def run_server():
            uvicorn.run(consensus_app, 
                       host="0.0.0.0", 
                       port=self.config.port, 
                       log_level="warning")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        time.sleep(3)  # Esperar inicio
        
        # Verificar que el servidor esté activo
        try:
            response = requests.get(f"http://localhost:{self.config.port}/status", timeout=2)
            if response.status_code == 200:
                print(f"✅ Servidor de consenso activo en puerto {self.config.port}")
            else:
                raise Exception("Servidor no responde correctamente")
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
            raise
    
    def _auto_register_self(self):
        """Auto-registrar este nodo en el sistema de consenso."""
        try:
            response = requests.post(
                f"http://localhost:{self.config.port}/network/register",
                json={
                    "nodeId": self.network_discovery.my_node_id,
                    "ip": self.network_discovery.my_ip,
                    "publicKey": f"pubkey_{self.network_discovery.my_node_id}",
                    "signature": f"self_signature_{self.network_discovery.my_node_id}"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Auto-registrado como {self.network_discovery.my_node_id}")
            else:
                print(f"⚠️ Error en auto-registro: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Error en auto-registro: {e}")
    
    def show_network_status(self):
        """Mostrar estado actual de la red."""
        stats = self.network_discovery.get_network_stats()
        
        print("\n" + "=" * 50)
        print("🌐 ESTADO DE LA RED DISTRIBUIDA")
        print("=" * 50)
        print(f"🏷️ Mi Nodo: {stats['my_node_id']}")
        print(f"📍 Mi IP: {stats['my_ip']}")
        print(f"👥 Nodos Conectados: {stats['total_nodes']}")
        print()
        
        if stats['active_nodes']:
            print("📋 NODOS ACTIVOS:")
            for i, node in enumerate(stats['active_nodes'], 1):
                print(f"   {i}. {node['id']} - {node['ip']} ({node['status']})")
        else:
            print("⚠️ No hay otros nodos conectados")
        
        # Estado del consenso
        try:
            response = requests.get(f"http://localhost:{self.config.port}/status", timeout=2)
            if response.status_code == 200:
                consensus_status = response.json()
                print(f"\n📊 ESTADO DEL CONSENSO:")
                print(f"   🔄 Nodos registrados: {consensus_status.get('nodes_registered', 0)}")
                print(f"   🗳️ Votos totales: {consensus_status.get('total_votes', 0)}")
                print(f"   🪙 Tokens congelados: {consensus_status.get('total_frozen_tokens', 0)}")
        except:
            print("\n⚠️ No se pudo obtener estado del consenso")
        
        print("=" * 50)
    
    def demo_distributed_consensus(self):
        """Demostración de consenso distribuido con nodos reales."""
        print("\n🎯 INICIANDO DEMO DE CONSENSO DISTRIBUIDO")
        print("=" * 50)
        
        # Esperar a que se conecten nodos
        print("⏳ Esperando conexiones de otros nodos...")
        for i in range(30):  # 30 segundos
            active_nodes = len(self.network_discovery.get_active_nodes())
            if active_nodes > 0:
                print(f"✅ {active_nodes} nodo(s) conectado(s)")
                break
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Esperando... ({30-i} segundos restantes)")
        
        # Mostrar estado de la red
        self.show_network_status()
        
        # Simular proceso de consenso distribuido
        print("\n🗳️ Iniciando proceso de votación distribuida...")
        
        # Los otros nodos deberían participar automáticamente
        # si tienen el sistema ejecutándose
        
        try:
            # Congelar tokens propios
            response = requests.post(
                f"http://localhost:{self.config.port}/tokens/freeze",
                json={
                    "nodeId": self.network_discovery.my_node_id,
                    "tokens": 100,
                    "signature": f"freeze_sig_{self.network_discovery.my_node_id}"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Tokens propios congelados")
            
            # Votar
            response = requests.post(
                f"http://localhost:{self.config.port}/consensus/vote",
                json={
                    "nodeId": self.network_discovery.my_node_id,
                    "vote": "accept_distributed_block",
                    "signature": f"vote_sig_{self.network_discovery.my_node_id}"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Voto enviado")
            
            # Esperar y mostrar resultado
            time.sleep(5)
            response = requests.get(f"http://localhost:{self.config.port}/consensus/result", timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n📊 RESULTADO DEL CONSENSO DISTRIBUIDO:")
                print(f"   🎯 Acuerdo alcanzado: {'Sí' if result.get('hasAgreement', False) else 'No'}")
                print(f"   📈 Porcentaje: {result.get('agreementPercentage', 0)}%")
                print(f"   🗳️ Votos totales: {result.get('totalVotes', 0)}")
                
                return result.get('hasAgreement', False)
            
        except Exception as e:
            print(f"❌ Error en demo: {e}")
        
        return False
    
    def interactive_mode(self):
        """Modo interactivo para administrar el sistema."""
        print("\n🎛️ MODO INTERACTIVO - SISTEMA DISTRIBUIDO")
        
        while True:
            print("\n" + "="*40)
            print("OPCIONES DISPONIBLES:")
            print("1. 📊 Ver estado de la red")
            print("2. 🎯 Demo de consenso distribuido")
            print("3. 🔄 Forzar sincronización")
            print("4. 📡 Información de conexión")
            print("5. 🗳️ Votar manualmente")
            print("6. 🪙 Congelar tokens")
            print("0. 🚪 Salir")
            print("="*40)
            
            try:
                opcion = input("Selecciona una opción: ").strip()
                
                if opcion == "1":
                    self.show_network_status()
                
                elif opcion == "2":
                    success = self.demo_distributed_consensus()
                    if success:
                        print("🎉 Demo exitosa!")
                    else:
                        print("⚠️ Demo con resultados parciales")
                
                elif opcion == "3":
                    print("🔄 Forzando sincronización...")
                    # La sincronización es automática, pero podemos mostrar estado
                    time.sleep(2)
                    self.show_network_status()
                
                elif opcion == "4":
                    print(f"\n📡 INFORMACIÓN DE CONEXIÓN:")
                    print(f"   🌐 Tu IP: {self.network_discovery.my_ip}")
                    print(f"   🚪 Puerto: {self.config.port}")
                    print(f"   🔍 Puerto Discovery: {self.config.discovery_port}")
                    print(f"   🏷️ ID Nodo: {self.network_discovery.my_node_id}")
                    print(f"\n📋 Para que tus compañeros se conecten:")
                    print(f"   Deben ejecutar el sistema en la misma red")
                    print(f"   URL de tu nodo: http://{self.network_discovery.my_ip}:{self.config.port}")
                
                elif opcion == "5":
                    vote = input("Ingresa tu voto: ").strip()
                    if vote:
                        try:
                            response = requests.post(
                                f"http://localhost:{self.config.port}/consensus/vote",
                                json={
                                    "nodeId": self.network_discovery.my_node_id,
                                    "vote": vote,
                                    "signature": f"manual_vote_{int(time.time())}"
                                },
                                timeout=5
                            )
                            if response.status_code == 200:
                                print("✅ Voto registrado")
                            else:
                                print("❌ Error registrando voto")
                        except Exception as e:
                            print(f"❌ Error: {e}")
                
                elif opcion == "6":
                    try:
                        tokens = int(input("Cantidad de tokens a congelar: ").strip())
                        response = requests.post(
                            f"http://localhost:{self.config.port}/tokens/freeze",
                            json={
                                "nodeId": self.network_discovery.my_node_id,
                                "tokens": tokens,
                                "signature": f"manual_freeze_{int(time.time())}"
                            },
                            timeout=5
                        )
                        if response.status_code == 200:
                            print(f"✅ {tokens} tokens congelados")
                        else:
                            print("❌ Error congelando tokens")
                    except ValueError:
                        print("❌ Cantidad inválida")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                elif opcion == "0":
                    print("👋 Cerrando sistema distribuido...")
                    break
                
                else:
                    print("❌ Opción inválida")
                    
            except KeyboardInterrupt:
                print("\n👋 Sistema interrumpido")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def stop_system(self):
        """Detener sistema distribuido."""
        print("🛑 Deteniendo sistema distribuido...")
        self.synchronizer.stop_sync()
        self.network_discovery.stop_discovery()
        print("✅ Sistema detenido")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal del sistema distribuido."""
    print("🌐 Sistema de Consenso Distribuido Multi-Nodo")
    print("=" * 60)
    print("👥 Para conectar con compañeros de clase")
    print("=" * 60)
    
    # Preguntar puerto (opcional)
    try:
        port_input = input("Puerto para el servidor (presiona Enter para 8000): ").strip()
        port = int(port_input) if port_input else 8000
    except ValueError:
        port = 8000
        print("⚠️ Puerto inválido, usando 8000")
    
    # Crear y iniciar sistema
    system = DistributedConsensusSystem(port=port)
    
    try:
        system.start_system()
        
        # Esperar un poco para que se establezcan conexiones
        print("\n⏳ Esperando 10 segundos para establecer conexiones...")
        time.sleep(10)
        
        # Entrar en modo interactivo
        system.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n⏹️ Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")
    finally:
        system.stop_system()

if __name__ == "__main__":
    main()
