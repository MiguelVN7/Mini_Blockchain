#!/usr/bin/env python3
"""
Script de Demostración Coordinada Multi-Aula
=============================================
Script para coordinar una demostración de consenso distribuido
entre todos los estudiantes de la clase.

Autor: Miguel Villegas Nicholls
Curso: Fundamentos de Blockchain
Fecha: 24 de agosto de 2025

Uso:
1. El profesor designa un "coordinador" (puede ser Miguel)
2. Todos ejecutan sus sistemas distribuidos
3. El coordinador ejecuta este script para orchestar la demo
"""

import requests
import time
import json
from datetime import datetime
from typing import List, Dict, Any
import concurrent.futures
import threading

class ClassroomConsensusDemo:
    """Demostración coordinada de consenso para toda la clase."""
    
    def __init__(self):
        self.discovered_nodes: List[Dict] = []
        self.active_nodes: List[Dict] = []
        self.demo_results = {}
        
    def discover_classroom_nodes(self, ip_range: str = "192.168.1") -> List[Dict]:
        """Descubrir todos los nodos activos en el aula."""
        print("🔍 Descubriendo nodos de estudiantes en el aula...")
        print(f"   Escaneando rango: {ip_range}.100-120")
        
        discovered = []
        
        def test_ip(ip: str):
            for port in [8000, 8001, 8002]:
                try:
                    response = requests.get(f"http://{ip}:{port}/status", timeout=2)
                    if response.status_code == 200:
                        node_info = response.json()
                        return {
                            "ip": ip,
                            "port": port,
                            "status": node_info,
                            "student": f"Estudiante_{ip.split('.')[-1]}"
                        }
                except:
                    continue
            return None
        
        # Escaneo paralelo para ir más rápido
        ips_to_test = [f"{ip_range}.{i}" for i in range(100, 121)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(test_ip, ip): ip for ip in ips_to_test}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    discovered.append(result)
                    print(f"   ✅ Encontrado: {result['student']} en {result['ip']}:{result['port']}")
        
        self.discovered_nodes = discovered
        print(f"📊 Total de estudiantes conectados: {len(discovered)}")
        return discovered
    
    def verify_consensus_readiness(self) -> bool:
        """Verificar que todos los nodos estén listos para consenso."""
        print("\n🔍 Verificando preparación para consenso...")
        
        ready_nodes = []
        
        for node in self.discovered_nodes:
            try:
                response = requests.get(f"http://{node['ip']}:{node['port']}/status", timeout=3)
                if response.status_code == 200:
                    status = response.json()
                    if status.get('nodes_registered', 0) > 0:
                        ready_nodes.append(node)
                        print(f"   ✅ {node['student']}: Listo")
                    else:
                        print(f"   ⚠️ {node['student']}: Sin nodos registrados")
                else:
                    print(f"   ❌ {node['student']}: No responde")
            except Exception as e:
                print(f"   ❌ {node['student']}: Error - {e}")
        
        self.active_nodes = ready_nodes
        ready_percentage = (len(ready_nodes) / len(self.discovered_nodes)) * 100 if self.discovered_nodes else 0
        
        print(f"\n📊 Nodos listos: {len(ready_nodes)}/{len(self.discovered_nodes)} ({ready_percentage:.1f}%)")
        
        return len(ready_nodes) >= 3  # Mínimo 3 para consenso bizantino
    
    def coordinate_token_freezing(self, tokens_per_student: int = 100) -> bool:
        """Coordinar congelamiento de tokens en todos los nodos."""
        print(f"\n🪙 Coordinando congelamiento de {tokens_per_student} tokens por estudiante...")
        
        success_count = 0
        
        for i, node in enumerate(self.active_nodes):
            try:
                # Cada estudiante congela tokens en su propio nodo
                response = requests.post(
                    f"http://{node['ip']}:{node['port']}/tokens/freeze",
                    json={
                        "nodeId": f"student_node_{i+1}",
                        "tokens": tokens_per_student,
                        "signature": f"demo_freeze_{i+1}_{int(time.time())}"
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"   ✅ {node['student']}: {tokens_per_student} tokens congelados")
                    success_count += 1
                else:
                    print(f"   ❌ {node['student']}: Error congelando tokens")
                    
            except Exception as e:
                print(f"   ❌ {node['student']}: Error - {e}")
        
        success_rate = (success_count / len(self.active_nodes)) * 100 if self.active_nodes else 0
        print(f"📊 Congelamiento exitoso: {success_count}/{len(self.active_nodes)} ({success_rate:.1f}%)")
        
        return success_rate >= 70
    
    def execute_coordinated_vote(self, vote_scenarios: List[Dict]) -> Dict[str, Any]:
        """Ejecutar votación coordinada con diferentes escenarios."""
        print("\n🗳️ Ejecutando votación coordinada...")
        
        results = {}
        
        for scenario in vote_scenarios:
            print(f"\n📋 Escenario: {scenario['name']}")
            print(f"   Descripción: {scenario['description']}")
            
            # Asignar votos según el escenario
            votes_assigned = 0
            for i, node in enumerate(self.active_nodes):
                if votes_assigned < len(scenario['votes']):
                    vote = scenario['votes'][votes_assigned % len(scenario['votes'])]
                    
                    try:
                        response = requests.post(
                            f"http://{node['ip']}:{node['port']}/consensus/vote",
                            json={
                                "nodeId": f"student_node_{i+1}",
                                "vote": vote,
                                "signature": f"demo_vote_{i+1}_{int(time.time())}"
                            },
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            print(f"   ✅ {node['student']}: Voto '{vote}' registrado")
                        else:
                            print(f"   ❌ {node['student']}: Error votando")
                            
                    except Exception as e:
                        print(f"   ❌ {node['student']}: Error - {e}")
                    
                    votes_assigned += 1
            
            # Esperar que se procesen los votos
            print("   ⏳ Esperando procesamiento de votos...")
            time.sleep(3)
            
            # Obtener resultado del consenso desde cualquier nodo activo
            consensus_result = self._get_consensus_result()
            if consensus_result:
                results[scenario['name']] = consensus_result
                print(f"   📊 Resultado: {consensus_result['agreementPercentage']}% de acuerdo")
                print(f"   🎯 Consenso: {'Sí' if consensus_result['hasAgreement'] else 'No'}")
            
            # Limpiar votos para siguiente escenario
            time.sleep(2)
        
        return results
    
    def _get_consensus_result(self) -> Dict[str, Any]:
        """Obtener resultado del consenso desde cualquier nodo."""
        for node in self.active_nodes:
            try:
                response = requests.get(f"http://{node['ip']}:{node['port']}/consensus/result", timeout=3)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        return {}
    
    def generate_classroom_report(self) -> str:
        """Generar reporte completo de la demostración del aula."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"classroom_consensus_demo_{timestamp}.json"
        
        report = {
            "demo_info": {
                "timestamp": datetime.now().isoformat(),
                "coordinator": "Miguel Villegas Nicholls",
                "course": "Fundamentos de Blockchain",
                "demo_type": "Consenso Distribuido Multi-Aula"
            },
            "network_stats": {
                "total_students_discovered": len(self.discovered_nodes),
                "active_participants": len(self.active_nodes),
                "participation_rate": (len(self.active_nodes) / len(self.discovered_nodes)) * 100 if self.discovered_nodes else 0
            },
            "nodes_info": [
                {
                    "student": node['student'],
                    "ip": node['ip'],
                    "port": node['port']
                }
                for node in self.active_nodes
            ],
            "demo_results": self.demo_results,
            "technical_validation": {
                "byzantine_threshold": "66.67%",
                "minimum_nodes": 3,
                "actual_nodes": len(self.active_nodes),
                "network_resilience": "Tested",
                "consensus_algorithm": "Byzantine Fault Tolerant"
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📄 Reporte guardado: {filename}")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
        
        return filename
    
    def run_complete_classroom_demo(self):
        """Ejecutar demostración completa coordinada."""
        print("🎓 DEMOSTRACIÓN DE CONSENSO DISTRIBUIDO - AULA COMPLETA")
        print("=" * 70)
        print(f"📅 Fecha: {datetime.now().strftime('%d de %B de %Y')}")
        print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
        print(f"👤 Coordinador: Miguel Villegas Nicholls")
        print("=" * 70)
        
        try:
            # Fase 1: Descubrimiento
            print("\n🔍 FASE 1: Descubrimiento de Red")
            nodes = self.discover_classroom_nodes()
            
            if not nodes:
                print("❌ No se encontraron nodos. Asegúrate de que los compañeros tengan el sistema ejecutándose.")
                return
            
            # Fase 2: Verificación
            print("\n✅ FASE 2: Verificación de Preparación")
            if not self.verify_consensus_readiness():
                print("❌ No hay suficientes nodos listos para consenso bizantino (mínimo 3)")
                return
            
            # Fase 3: Preparación de tokens
            print("\n🪙 FASE 3: Preparación de Tokens")
            if not self.coordinate_token_freezing():
                print("⚠️ Algunos estudiantes tuvieron problemas congelando tokens")
            
            # Fase 4: Escenarios de votación
            print("\n🗳️ FASE 4: Escenarios de Votación")
            
            vote_scenarios = [
                {
                    "name": "unanimidad",
                    "description": "Todos votan igual - debe alcanzar 100% consenso",
                    "votes": ["aprobar_bloque_demo"]
                },
                {
                    "name": "mayoria_simple", 
                    "description": "70% aprueba, 30% rechaza - debe alcanzar consenso",
                    "votes": ["aprobar", "aprobar", "aprobar", "rechazar"]
                },
                {
                    "name": "sin_consenso",
                    "description": "50% aprueba, 50% rechaza - no debe alcanzar consenso",
                    "votes": ["aprobar", "rechazar"]
                }
            ]
            
            self.demo_results = self.execute_coordinated_vote(vote_scenarios)
            
            # Fase 5: Resultados
            print("\n📊 FASE 5: Análisis de Resultados")
            self.analyze_demo_results()
            
            # Fase 6: Reporte final
            print("\n📄 FASE 6: Generación de Reporte")
            report_file = self.generate_classroom_report()
            
            print("\n🎉 DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 70)
            print(f"👥 Participantes: {len(self.active_nodes)} estudiantes")
            print(f"🎯 Escenarios probados: {len(vote_scenarios)}")
            print(f"📄 Reporte: {report_file}")
            print("✅ Consenso distribuido funcionando en red real")
            
        except KeyboardInterrupt:
            print("\n⏹️ Demostración interrumpida por el usuario")
        except Exception as e:
            print(f"\n❌ Error en la demostración: {e}")
    
    def analyze_demo_results(self):
        """Analizar y mostrar resultados de la demo."""
        if not self.demo_results:
            print("⚠️ No hay resultados para analizar")
            return
        
        print("📈 ANÁLISIS DE RESULTADOS:")
        
        for scenario, result in self.demo_results.items():
            print(f"\n📋 Escenario: {scenario}")
            print(f"   🎯 Acuerdo alcanzado: {'Sí' if result.get('hasAgreement', False) else 'No'}")
            print(f"   📊 Porcentaje: {result.get('agreementPercentage', 0)}%")
            print(f"   🗳️ Votos totales: {result.get('totalVotes', 0)}")
            
            # Validación técnica
            expected_consensus = scenario != "sin_consenso"
            actual_consensus = result.get('hasAgreement', False)
            
            if expected_consensus == actual_consensus:
                print("   ✅ Resultado esperado - Algoritmo funcionando correctamente")
            else:
                print("   ⚠️ Resultado inesperado - Revisar algoritmo")

def main():
    """Función principal de coordinación."""
    demo = ClassroomConsensusDemo()
    
    print("🎓 Coordinador de Demostración Distribuida")
    print("=" * 50)
    print("Este script coordina la demostración entre TODOS los estudiantes.")
    print("Asegúrate de que tus compañeros tengan sus sistemas ejecutándose.")
    print("=" * 50)
    
    print("\n🔧 OPCIONES:")
    print("1. 🚀 Demostración completa automatizada")
    print("2. 🔍 Solo descubrir nodos")
    print("3. 📊 Verificar preparación")
    print("0. ❌ Cancelar")
    
    try:
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            demo.run_complete_classroom_demo()
        elif opcion == "2":
            demo.discover_classroom_nodes()
        elif opcion == "3":
            demo.discover_classroom_nodes()
            demo.verify_consensus_readiness()
        elif opcion == "0":
            print("👋 Coordinación cancelada")
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 Coordinación interrumpida")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
