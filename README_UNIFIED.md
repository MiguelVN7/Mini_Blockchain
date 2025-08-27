# 🎓 Protocolo de Consenso Blockchain - Implementación Unificada

### ✅ **Cumplimiento EXACTO de Especificación del Protocolo**

**1. Algoritmo de Selección de Líder**
```python
# Direcciones IP convertidas a números de 32-bit, mayor primero
def _ip_to_32bit(self, ip: str) -> int:
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

# Rotación determinística: primer líder = IP mayor, segundo = siguiente mayor, etc.
sorted_nodes = sorted(active_nodes, key=lambda x: x.ip_as_32bit, reverse=True)
```

**2. Congelamiento de Tokens con Firmas Digitales**
```python
# Cada miembro firma digitalmente su decisión de congelamiento de tokens
freeze_data = f"{node_id}{tokens}{timestamp}".encode()
if not self.crypto.verify_signature(node.public_key, freeze_data, signature):
    return False
```

**3. Generación de Número de Consenso de 32-bit**
```python
# Primeros 2 bytes: número de ronda (0-65,535, luego reinicia)
round_bytes = self.state.current_round & 0xFFFF
# Últimos 2 bytes: RNG de Python uniforme [0, 2^16-1]
random_bytes = random.randint(0, 0xFFFF)
consensus_number = (round_bytes << 16) | random_bytes
```

**4. Selección Aleatoria Ponderada**
```python
# Probabilidad proporcional a tokens congelados usando semilla de consenso
random.seed(consensus_number)
total_tokens = sum(self.state.frozen_tokens.values())
rand_value = random.randint(0, total_tokens - 1)
# Seleccionar líder basado en pesos acumulativos de tokens
```

**5. Consenso Bizantino 2/3**
```python
# Requerir 66.67% de acuerdo ponderado por tokens
agreement_percentage = (winning_votes / total_weight) * 100
has_consensus = agreement_percentage >= 66.67
```

**6. Validación de Bloques y Detección de Fraudes**
```python
# Confirmación 2/3 para expulsión de líder
if total_reporters >= (total_nodes * 2) // 3:
    self.state.nodes[fraudulent_id].is_active = False
```

## 🚀 **Inicio Rápido (30 segundos)**

### **Opción 1: Demostración Completa**
```bash
python3 blockchain_consensus_unified.py
# Seleccionar: 1 (Demostración automatizada completa)
```

### **Opción 2: Modo Servidor API**
```bash
python3 blockchain_consensus_unified.py  
# Seleccionar: 2 (Solo iniciar servidor API)
# Luego visitar: http://localhost:8000/docs
```

### **Instalación de Dependencias**
```bash
pip install fastapi uvicorn pydantic
```


## 📋 **Lista de Verificación del Protocolo**

- [x] **Selección de Líder**: Rotación determinística basada en IP ✅
- [x] **Congelamiento de Tokens**: Verificación de firma digital ✅  
- [x] **Número de Consenso**: Estructura de 32-bit (ronda + aleatorio) ✅
- [x] **Selección Ponderada**: Probabilidad proporcional a tokens ✅
- [x] **Consenso Bizantino**: Umbral de mayoría 2/3 ✅
- [x] **Validación de Bloques**: Minado aprobado por consenso ✅
- [x] **Detección de Fraudes**: Mecanismo de expulsión de líder ✅
- [x] **Persistencia de Estado**: Recuperación de estado basada en JSON ✅

## 📊 **Endpoints de API (Todos Funcionales)**

| Método | Endpoint | Funcionalidad |
|--------|----------|---------------|
| GET | `/status` | Estado completo del sistema |
| POST | `/network/register` | Registrar nodo de red |
| POST | `/tokens/freeze` | Congelar tokens con firma |
| POST | `/consensus/generate-number` | Líder genera número de consenso |
| POST | `/consensus/vote` | Enviar voto cifrado |
| GET | `/consensus/result` | Obtener resultado de consenso |
| POST | `/block/validate` | Validar bloque a través de consenso |
| POST | `/network/report-fraud` | Reportar comportamiento fraudulento |

**Todos los endpoints incluyen:**
- ✅ Verificación de firma digital
- ✅ Validación de cumplimiento del protocolo  
- ✅ Manejo integral de errores
- ✅ Documentación automática de API

