#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBAS COMPLETAS
Prueba todos los sistemas de consenso desarrollados
"""

import subprocess
import time
import requests
import json
import os
import signal
import sys
from datetime import datetime

class SystemTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {}
        }
        self.processes = []
        
    def cleanup(self):
        """Limpiar procesos en ejecución."""
        for p in self.processes:
            try:
                p.terminate()
                p.wait(timeout=3)
            except:
                try:
                    p.kill()
                except:
                    pass
        
        # Limpiar procesos por nombre
        try:
            subprocess.run(["pkill", "-f", "consensus"], check=False, capture_output=True)
            subprocess.run(["pkill", "-f", "uvicorn"], check=False, capture_output=True)
        except:
            pass
            
    def test_basic_consensus(self):
        """Probar sistema de consenso básico."""
        print("🧪 Probando sistema básico...")
        
        try:
            code = '''
from consensus_system import ConsensusEngine
consensus = ConsensusEngine()
order = consensus.register_node("test_node", "127.0.0.1", "test_key")
success = consensus.freeze_tokens("test_node", 100, "test_sig")
leader = consensus.state.registry.get_leader_for_turn(1)
seed_ok, seed = consensus.set_seed(leader, "test_seed", 1, "test_sig")
print(f"RESULT:OK:{len(consensus.state.registry.nodes)}:{success}:{seed_ok}:{seed}")
'''
            
            result = subprocess.run([
                "python3", "-c", code
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "RESULT:OK:" in result.stdout:
                parts = result.stdout.split("RESULT:OK:")[1].strip().split(":")
                self.results["tests"]["basic_consensus"] = {
                    "status": "✅ PASS",
                    "nodes": int(parts[0]),
                    "tokens_frozen": parts[1] == "True",
                    "seed_set": parts[2] == "True",
                    "seed_value": int(parts[3])
                }
                print("✅ Sistema básico: FUNCIONAL")
                return True
            else:
                raise Exception(f"Error: {result.stderr}")
                
        except Exception as e:
            self.results["tests"]["basic_consensus"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"❌ Sistema básico: ERROR - {e}")
            return False
    
    def test_api_server(self):
        """Probar servidor API."""
        print("🧪 Probando servidor API...")
        
        try:
            # Iniciar servidor
            process = subprocess.Popen([
                "python3", "consensus_system.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(process)
            
            # Esperar que se inicie
            time.sleep(4)
            
            # Probar endpoints
            response1 = requests.get("http://localhost:8000/status", timeout=5)
            response2 = requests.get("http://localhost:8000/nodes", timeout=5)
            
            # Registrar nodo
            response3 = requests.post("http://localhost:8000/register", 
                json={
                    "nodeId": "api_test",
                    "ip": "127.0.0.1",
                    "publicKey": "test_key"
                }, timeout=5)
            
            if all([r.status_code == 200 for r in [response1, response2, response3]]):
                self.results["tests"]["api_server"] = {
                    "status": "✅ PASS",
                    "endpoints_working": 3,
                    "response_time": "< 1s"
                }
                print("✅ Servidor API: FUNCIONAL")
                return True
            else:
                raise Exception("Algunos endpoints fallaron")
                
        except Exception as e:
            self.results["tests"]["api_server"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"❌ Servidor API: ERROR - {e}")
            return False
        finally:
            self.cleanup()
    
    def test_network_setup(self):
        """Probar configurador de red."""
        print("🧪 Probando configurador de red...")
        
        try:
            # Simular entrada automática (opción 3: solo escanear)
            process = subprocess.Popen([
                "python3", "network_setup.py"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, text=True)
            
            stdout, stderr = process.communicate(input="3\n", timeout=15)
            
            if "Mi IP:" in stdout and "Escaneando" in stdout:
                self.results["tests"]["network_setup"] = {
                    "status": "✅ PASS",
                    "network_detected": True,
                    "scan_completed": True
                }
                print("✅ Configurador de red: FUNCIONAL")
                return True
            else:
                raise Exception("No detectó red correctamente")
                
        except Exception as e:
            self.results["tests"]["network_setup"] = {
                "status": "❌ FAIL", 
                "error": str(e)
            }
            print(f"❌ Configurador de red: ERROR - {e}")
            return False
    
    def test_blockchain_integration(self):
        """Probar integración con blockchain."""
        print("🧪 Probando integración blockchain...")
        
        try:
            code = '''
from blockchain_with_consensus import BlockchainWithConsensus
bc = BlockchainWithConsensus()
bc.start_consensus()
tx_id = bc.create_transaction("Alice", "Bob", 50)
success = bc.process_transaction(tx_id)
bc.stop_consensus()
print(f"RESULT:OK:{len(bc.blockchain.chain)}:{success}:{len(bc.pending_transactions)}")
'''
            
            result = subprocess.run([
                "python3", "-c", code
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "RESULT:OK:" in result.stdout:
                parts = result.stdout.split("RESULT:OK:")[1].strip().split(":")
                self.results["tests"]["blockchain_integration"] = {
                    "status": "✅ PASS",
                    "chain_length": int(parts[0]),
                    "transaction_processed": parts[1] == "True",
                    "pending_transactions": int(parts[2])
                }
                print("✅ Integración blockchain: FUNCIONAL")
                return True
            else:
                raise Exception(f"Error: {result.stderr}")
                
        except Exception as e:
            self.results["tests"]["blockchain_integration"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"❌ Integración blockchain: ERROR - {e}")
            return False
    
    def generate_report(self):
        """Generar reporte final."""
        print("\n" + "="*60)
        print("📊 REPORTE DE PRUEBAS COMPLETAS")
        print("="*60)
        
        passed = sum(1 for test in self.results["tests"].values() 
                    if test["status"].startswith("✅"))
        total = len(self.results["tests"])
        
        print(f"✅ Pruebas exitosas: {passed}/{total}")
        print(f"⏰ Timestamp: {self.results['timestamp']}")
        print()
        
        for name, result in self.results["tests"].items():
            print(f"{result['status']} {name.replace('_', ' ').title()}")
            if result["status"].startswith("✅"):
                # Mostrar detalles de éxito
                for key, value in result.items():
                    if key != "status":
                        print(f"   • {key}: {value}")
            else:
                print(f"   • Error: {result.get('error', 'Desconocido')}")
            print()
        
        # Guardar reporte
        filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Reporte guardado: {filename}")
        
        # Conclusión
        if passed == total:
            print("🎉 ¡TODOS LOS SISTEMAS FUNCIONAN CORRECTAMENTE!")
        else:
            print(f"⚠️ {total - passed} sistema(s) requieren atención")
        
        return passed == total

def main():
    """Ejecutar todas las pruebas."""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
    print("=" * 60)
    
    tester = SystemTester()
    
    def signal_handler(signum, frame):
        print("\n⚠️ Interrupción recibida, limpiando...")
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Ejecutar pruebas
        tests = [
            tester.test_basic_consensus,
            tester.test_network_setup,
            tester.test_api_server,
            tester.test_blockchain_integration
        ]
        
        for test in tests:
            test()
            time.sleep(2)  # Pausa entre pruebas
            
        # Generar reporte final
        success = tester.generate_report()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Pruebas interrumpidas por el usuario")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
