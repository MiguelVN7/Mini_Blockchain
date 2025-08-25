# 🌐 Guía para Conexión Multi-Dispositivo

**Sistema:** Consenso Distribuido Real entre Compañeros  
**Autor:** Miguel Villegas Nicholls  
**Fecha:** 24 de agosto de 2025

## 🎯 Objetivo

Conectar el sistema de consenso con los computadores de todos tus compañeros de clase para crear una **red blockchain distribuida real**.

## 📋 Requisitos Previos

### Para cada estudiante:
1. **Python 3.8+** instalado
2. **Misma red WiFi** (universidad/aula)
3. **Puertos abiertos:** 8000 y 8001
4. **Archivos del sistema:** `consensus_system.py` y `distributed_consensus_system.py`

## 🚀 Instrucciones de Configuración

### Paso 1: Preparación Individual

Cada estudiante debe tener estos archivos:
```
Mi_Proyecto/
├── consensus_system.py           # Sistema base
├── distributed_consensus_system.py  # Sistema distribuido
└── network_setup.py             # Script de configuración (crear abajo)
```

### Paso 2: Verificar Conectividad de Red

**Comando para verificar IP local:**
```bash
# En macOS/Linux:
ifconfig | grep "inet "

# En Windows:
ipconfig
```

**Ejemplo de IPs en aula:**
- Estudiante A: `192.168.1.101`
- Estudiante B: `192.168.1.102`
- Estudiante C: `192.168.1.103`
- etc.

### Paso 3: Ejecutar Sistema Distribuido

**En cada computador ejecutar:**
```bash
python3 distributed_consensus_system.py
```

**El sistema automáticamente:**
1. ✅ Detecta su propia IP
2. ✅ Crea un ID único para el nodo
3. ✅ Inicia servidor en puerto 8000
4. ✅ Busca otros nodos en la red
5. ✅ Se conecta automáticamente

## 🔧 Configuración Avanzada

### Personalizar Puerto (si hay conflictos)
```bash
python3 distributed_consensus_system.py
# Cuando pregunte el puerto, usar: 8001, 8002, etc.
```

### Verificar Conexiones
Una vez iniciado, usar la opción "1" en el menú para ver:
- Nodos conectados
- Estado de la red
- Estadísticas de consenso

## 🎯 Flujo de Demostración Colaborativa

### Fase 1: Conexión (2-3 minutos)
1. **Profesor coordina:** "Todos ejecuten el sistema ahora"
2. **Estudiantes ejecutan:** `python3 distributed_consensus_system.py`
3. **Verifican conexiones:** Opción "1" - Ver estado de red
4. **Confirman:** Cada uno ve a los demás conectados

### Fase 2: Consenso Colaborativo (5 minutos)
1. **Coordinador (puedes ser tú):** Inicia demo con opción "2"
2. **Todos participan:** El sistema automáticamente incluye a todos
3. **Votación distribuida:** Cada nodo vota automáticamente
4. **Resultado conjunto:** Se muestra el consenso de toda la clase

### Fase 3: Interacción Manual (10 minutos)
1. **Votación manual:** Opción "5" - cada uno vota diferente
2. **Congelación tokens:** Opción "6" - diferentes cantidades
3. **Ver resultados:** Opción "1" - estado actualizado de toda la red
4. **Consenso final:** Verificar que el umbral 2/3 funciona

## 📊 Escenarios de Prueba

### Escenario 1: Consenso Unánime
- **Todos votan:** "aprobar_bloque_123"
- **Resultado esperado:** 100% de acuerdo
- **Demostración:** Sistema funciona perfectamente

### Escenario 2: Mayoría Simple
- **70% vota:** "aprobar"
- **30% vota:** "rechazar"  
- **Resultado esperado:** 70% de acuerdo (>66.67% requerido)
- **Demostración:** Consenso bizantino exitoso

### Escenario 3: Sin Consenso
- **50% vota:** "aprobar"
- **50% vota:** "rechazar"
- **Resultado esperado:** 50% de acuerdo (<66.67% requerido)
- **Demostración:** Sistema rechaza correctamente

### Escenario 4: Nodos Maliciosos
- **Algunos nodos** se desconectan o votan aleatoriamente
- **Resultado esperado:** Sistema continúa funcionando
- **Demostración:** Tolerancia a fallos bizantinos

## 🛠️ Solución de Problemas

### Problema: "No se conectan otros nodos"
**Soluciones:**
1. Verificar misma red WiFi
2. Desactivar firewall temporalmente
3. Usar puertos alternativos (8001, 8002)
4. Verificar IP con `ifconfig`

### Problema: "Puerto ocupado"
**Solución:**
```bash
# Matar procesos previos
pkill -f "python3.*consensus"
# O usar puerto diferente en cada máquina
```

### Problema: "Consenso no funciona"
**Verificar:**
1. Todos tienen tokens congelados
2. Votos están siendo registrados
3. Al menos 3 nodos participando

## 📡 Información Técnica

### Puertos Utilizados
- **8000:** Servidor de consenso principal
- **8001:** Descubrimiento automático de nodos
- **Broadcast UDP:** Para encontrar nodos automáticamente

### Protocolo de Comunicación
1. **Descubrimiento:** Broadcast UDP cada 30 segundos
2. **Consenso:** API HTTP REST entre nodos
3. **Sincronización:** Estado compartido cada 15 segundos

### Seguridad Básica
- Firmas digitales simuladas (GPG en producción)
- Validación de nodos por IP
- Timeouts para nodos inactivos

## 🎓 Para el Profesor

### Evaluación de la Demo
**Observar:**
1. ✅ **Conectividad:** ¿Se conectan automáticamente?
2. ✅ **Descubrimiento:** ¿Se encuentran todos los nodos?
3. ✅ **Consenso:** ¿Funciona el algoritmo bizantino?
4. ✅ **Tolerancia:** ¿Resiste desconexiones?
5. ✅ **Sincronización:** ¿Se mantiene estado consistente?

### Puntos de Evaluación
- **Técnico:** Implementación de red P2P real
- **Funcional:** Consenso distribuido operativo
- **Colaborativo:** Trabajo en equipo efectivo
- **Robusto:** Manejo de errores y fallos

## 🏆 Resultado Esperado

**Al final de la demostración deberían tener:**
- ✅ Red de 10-20 nodos (estudiantes) conectados
- ✅ Consenso distribuido funcionando en tiempo real
- ✅ Votación colaborativa exitosa
- ✅ Evidencia de tolerancia bizantina
- ✅ Estadísticas de red completas

---

**🎯 Esta demostración prueba que tu sistema no solo funciona en teoría, sino que opera en una red distribuida real con múltiples participantes, tal como un blockchain verdadero.**
