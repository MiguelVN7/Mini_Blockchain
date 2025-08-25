#!/usr/bin/env python3
"""
Script de Configuración de Red Distribuida
==========================================
Herramienta auxiliar para preparar y verificar la conexión
entre múltiples dispositivos de estudiantes.

Autor: Miguel Villegas Nicholls
Curso: Fundamentos de Blockchain
Fecha: 24 de agosto de 2025
"""

import socket
import subprocess
import sys
import time
import json
import requests
from typing import List, Dict, Optional

class NetworkSetupHelper:
    """Ayudante para configurar red distribuida."""
    
    def __init__(self):
        self.my_ip = self._get_my_ip()
        self.common_ports = [8000, 8001, 8002, 8003]
        self.discovery_port = 8001
    
    def _get_my_ip(self) -> str:
        """Obtener IP local."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def check_network_requirements(self) -> Dict[str, bool]:
        """Verificar requisitos de red."""
        print("🔍 Verificando requisitos de red...")
        
        results = {
            "python_version": sys.version_info >= (3, 8),
            "network_accessible": self._test_network_access(),
            "ports_available": self._check_ports_available(),
            "required_files": self._check_required_files()
        }
        
        for requirement, status in results.items():
            symbol = "✅" if status else "❌"
            print(f"   {symbol} {requirement.replace('_', ' ').title()}")
        
        return results
    
    def _test_network_access(self) -> bool:
        """Probar acceso a la red."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    def _check_ports_available(self) -> bool:
        """Verificar puertos disponibles."""
        for port in self.common_ports[:2]:  # Solo verificar principales
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return True
            except:
                continue
        return False
    
    def _check_required_files(self) -> bool:
        """Verificar archivos requeridos."""
        import os
        required = ['consensus_system.py', 'distributed_consensus_system.py']
        return all(os.path.exists(f) for f in required)
    
    def scan_network_for_nodes(self, timeout: int = 5) -> List[Dict]:
        """Escanear la red buscando otros nodos."""
        print(f"🔍 Escaneando red local desde {self.my_ip}...")
        print("   Buscando otros estudiantes con el sistema activo...")
        
        # Obtener rango de red
        ip_parts = self.my_ip.split('.')
        network_base = '.'.join(ip_parts[:3])
        
        active_nodes = []
        
        # Escanear IPs comunes en el rango
        for i in range(100, 110):  # Rango común en aulas
            if i % 2 == 0:  # Solo pares para ir más rápido
                test_ip = f"{network_base}.{i}"
                if test_ip == self.my_ip:
                    continue
                
                node_info = self._test_node(test_ip, timeout=1)
                if node_info:
                    active_nodes.append(node_info)
                    print(f"   ✅ Nodo encontrado: {test_ip}")
        
        print(f"📊 Nodos encontrados: {len(active_nodes)}")
        return active_nodes
    
    def _test_node(self, ip: str, timeout: int = 1) -> Optional[Dict]:
        """Probar si hay un nodo activo en la IP."""
        for port in self.common_ports:
            try:
                response = requests.get(f"http://{ip}:{port}/status", 
                                      timeout=timeout)
                if response.status_code == 200:
                    return {
                        "ip": ip,
                        "port": port,
                        "status": response.json()
                    }
            except:
                continue
        return None
    
    def suggest_optimal_port(self) -> int:
        """Sugerir puerto óptimo para este nodo."""
        print("🔍 Buscando puerto óptimo...")
        
        for port in self.common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    print(f"✅ Puerto {port} disponible")
                    return port
            except:
                print(f"⚠️ Puerto {port} ocupado")
        
        # Si todos están ocupados, generar uno aleatorio
        import random
        random_port = random.randint(8010, 8050)
        print(f"🎲 Usando puerto aleatorio: {random_port}")
        return random_port
    
    def create_connection_info(self, port: int) -> Dict[str, str]:
        """Crear información de conexión para compartir."""
        return {
            "student_name": "Miguel Villegas Nicholls",  # Cambiar por cada estudiante
            "ip": self.my_ip,
            "port": port,
            "api_url": f"http://{self.my_ip}:{port}",
            "docs_url": f"http://{self.my_ip}:{port}/docs",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def test_connection_with_peer(self, peer_ip: str, peer_port: int = 8000) -> bool:
        """Probar conexión con un compañero específico."""
        print(f"🔗 Probando conexión con {peer_ip}:{peer_port}...")
        
        try:
            # Probar estado
            response = requests.get(f"http://{peer_ip}:{peer_port}/status", timeout=3)
            if response.status_code == 200:
                print("✅ Conexión exitosa")
                
                # Probar registro (simulado)
                test_register = requests.post(
                    f"http://{peer_ip}:{peer_port}/network/register",
                    json={
                        "nodeId": f"test_node_{int(time.time())}",
                        "ip": self.my_ip,
                        "publicKey": "test_pubkey",
                        "signature": "test_signature"
                    },
                    timeout=3
                )
                
                if test_register.status_code == 200:
                    print("✅ API de consenso funcionando")
                    return True
                else:
                    print("⚠️ Conexión OK, pero API con problemas")
                    return True
            
        except requests.exceptions.ConnectRefused:
            print("❌ Conexión rechazada - nodo no disponible")
        except requests.exceptions.Timeout:
            print("❌ Timeout - nodo no responde")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
        
        return False
    
    def interactive_setup(self):
        """Configuración interactiva paso a paso."""
        print("🎓 Configuración de Red Distribuida - Paso a Paso")
        print("=" * 60)
        
        # Paso 1: Verificar requisitos
        print("\n📋 PASO 1: Verificar Requisitos")
        requirements = self.check_network_requirements()
        
        if not all(requirements.values()):
            print("❌ Faltan requisitos. Revisar antes de continuar.")
            return
        
        print("✅ Todos los requisitos cumplidos")
        
        # Paso 2: Encontrar puerto
        print("\n🚪 PASO 2: Configurar Puerto")
        suggested_port = self.suggest_optimal_port()
        
        port_input = input(f"Puerto a usar (presiona Enter para {suggested_port}): ").strip()
        port = int(port_input) if port_input else suggested_port
        
        # Paso 3: Crear info de conexión
        print("\n📡 PASO 3: Información de Conexión")
        conn_info = self.create_connection_info(port)
        
        print("📋 Comparte esta información con tus compañeros:")
        print(f"   👤 Estudiante: {conn_info['student_name']}")
        print(f"   🌐 IP: {conn_info['ip']}")
        print(f"   🚪 Puerto: {conn_info['port']}")
        print(f"   🔗 URL API: {conn_info['api_url']}")
        
        # Paso 4: Buscar otros nodos
        print("\n🔍 PASO 4: Buscar Otros Nodos")
        scan_network = input("¿Escanear red buscando compañeros? (y/n): ").strip().lower()
        
        if scan_network == 'y':
            active_nodes = self.scan_network_for_nodes()
            if active_nodes:
                print("📋 Nodos encontrados:")
                for i, node in enumerate(active_nodes, 1):
                    print(f"   {i}. {node['ip']}:{node['port']}")
        
        # Paso 5: Probar conexión específica
        print("\n🔗 PASO 5: Probar Conexión con Compañero")
        test_connection = input("¿Probar conexión con IP específica? (y/n): ").strip().lower()
        
        if test_connection == 'y':
            peer_ip = input("IP del compañero: ").strip()
            peer_port = input("Puerto del compañero (Enter para 8000): ").strip()
            peer_port = int(peer_port) if peer_port else 8000
            
            if self.test_connection_with_peer(peer_ip, peer_port):
                print("🎉 Conexión exitosa con el compañero")
            else:
                print("⚠️ No se pudo conectar. Verificar que el compañero tenga el sistema ejecutándose")
        
        # Paso 6: Comandos finales
        print("\n🚀 PASO 6: Listo para Ejecutar")
        print("Comandos para ejecutar:")
        print(f"1. python3 distributed_consensus_system.py")
        print(f"   (Usar puerto {port} cuando pregunte)")
        print(f"2. O directamente: python3 -c \"import distributed_consensus_system; distributed_consensus_system.DistributedConsensusSystem({port}).start_system()\"")
        
        print("\n✅ Configuración completada")
        print("👥 Comparte tu IP con los compañeros para que se conecten")
    
    def quick_network_test(self):
        """Prueba rápida de red."""
        print("⚡ PRUEBA RÁPIDA DE RED")
        print("=" * 30)
        
        print(f"🌐 Mi IP: {self.my_ip}")
        print(f"🔍 Escaneando red...")
        
        active_nodes = self.scan_network_for_nodes(timeout=2)
        
        if active_nodes:
            print(f"✅ Encontrados {len(active_nodes)} nodos activos")
            print("🚀 Red lista para consenso distribuido")
        else:
            print("⚠️ No se encontraron otros nodos")
            print("💡 Asegúrate de que tus compañeros tengan el sistema ejecutándose")

def main():
    """Función principal."""
    helper = NetworkSetupHelper()
    
    print("🌐 Configurador de Red Distribuida")
    print("=" * 40)
    print("1. 🔧 Configuración completa (recomendado)")
    print("2. ⚡ Prueba rápida de red")
    print("3. 🔍 Solo escanear red")
    print("=" * 40)
    
    try:
        opcion = input("Selecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            helper.interactive_setup()
        elif opcion == "2":
            helper.quick_network_test()
        elif opcion == "3":
            helper.scan_network_for_nodes()
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 Configuración cancelada")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
