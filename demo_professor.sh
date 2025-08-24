#!/bin/bash

# 🎓 SCRIPT DE DEMOSTRACIÓN PARA EL PROFESOR
# Sistema de Consenso Distribuido - Miguel Villegas Nicholls
# Uso: ./demo_professor.sh

echo "🎓 DEMOSTRACIÓN PARA EL PROFESOR"
echo "Sistema de Consenso Distribuido - Miguel Villegas Nicholls"
echo "========================================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "consensus/api.py" ]; then
    echo "❌ Error: Ejecute este script desde el directorio 'Trabajo 1'"
    exit 1
fi

echo "📁 Directorio de trabajo: $(pwd)"
echo "📅 Fecha y hora: $(date)"
echo ""

# Paso 1: Iniciar servidor de consenso
echo "🚀 PASO 1: Iniciando servidor de consenso..."
echo "   Comando: python -m uvicorn consensus.api:app --host 0.0.0.0 --port 8000"
echo "   Puerto: http://localhost:8000"
echo "   Documentación: http://localhost:8000/docs"

# Detener servidor previo si existe
pkill -f "uvicorn.*consensus" 2>/dev/null || true
sleep 2

# Iniciar servidor en background
nohup python3 -m uvicorn consensus.api:app --host 0.0.0.0 --port 8000 > consensus_demo_server.log 2>&1 &
SERVER_PID=$!

echo "   ✅ Servidor iniciado (PID: $SERVER_PID)"
echo "   📋 Logs en: consensus_demo_server.log"
echo ""

# Esperar que el servidor esté listo
echo "⏳ Esperando que el servidor esté listo..."
sleep 5

# Verificar que el servidor responda
if curl -s http://localhost:8000/status > /dev/null; then
    echo "   ✅ Servidor respondiendo correctamente"
else
    echo "   ❌ Servidor no responde, revise los logs"
    echo "   💡 Comando para revisar logs: tail -f consensus_demo_server.log"
    exit 1
fi

echo ""

# Paso 2: Ejecutar demostración académica
echo "🎯 PASO 2: Ejecutando demostración académica completa..."
echo "   Esta demostración incluye:"
echo "   • Verificación de prerequisitos"
echo "   • Demostración de arquitectura"
echo "   • Pruebas de API REST"
echo "   • Workflow de consenso"
echo "   • Validación de requisitos académicos"
echo "   • Integración con blockchain"
echo ""

python3 academic_demonstration.py

echo ""
echo "📊 PASO 3: Información adicional para el profesor"
echo "========================================================"
echo ""

# Mostrar estado actual del sistema
echo "🔍 Estado actual del sistema:"
if curl -s http://localhost:8000/status | python3 -m json.tool; then
    echo "   ✅ Estado obtenido correctamente"
else
    echo "   ❌ Error obteniendo estado"
fi

echo ""

# Mostrar archivos generados
echo "📄 Archivos generados durante la demostración:"
ls -la academic_report_*.json 2>/dev/null || echo "   📝 No se generaron reportes (posible error en demostración)"
echo "   📋 Logs del servidor: consensus_demo_server.log"
echo "   💾 Estado del consenso: consensus_state.json"

echo ""

# Mostrar documentación de la API
echo "📚 ACCESO A LA DOCUMENTACIÓN:"
echo "   🌐 Documentación interactiva: http://localhost:8000/docs"
echo "   📊 Estado del sistema: http://localhost:8000/status"
echo "   🔗 API completa disponible en http://localhost:8000"

echo ""

# Instrucciones para el profesor
echo "👨‍🏫 INSTRUCCIONES PARA EL PROFESOR:"
echo "========================================"
echo ""
echo "1️⃣ VERIFICAR API EN VIVO:"
echo "   • Abrir navegador en: http://localhost:8000/docs"
echo "   • Explorar endpoints disponibles"
echo "   • Probar funcionalidades desde la interfaz web"
echo ""
echo "2️⃣ VERIFICAR ESTADO DEL SISTEMA:"
echo "   curl -s http://localhost:8000/status | python3 -m json.tool"
echo ""
echo "3️⃣ PROBAR REGISTRO DE NODOS:"
echo "   curl -X POST http://localhost:8000/network/register \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"nodeId\":\"test@example.com\",\"ip\":\"192.168.1.1\",\"publicKey\":\"test_key\",\"signature\":\"dGVzdA==\"}'"
echo ""
echo "4️⃣ REVISAR ARQUITECTURA DEL CÓDIGO:"
echo "   • consensus/api.py         - API REST con FastAPI"
echo "   • consensus/engine.py      - Lógica de consenso"
echo "   • consensus/models.py      - Modelos de datos"
echo "   • consensus/state.py       - Gestión de estado"
echo "   • consensus/crypto_provider.py - Criptografía GPG"
echo ""
echo "5️⃣ DETENER EL SISTEMA:"
echo "   pkill -f 'uvicorn.*consensus'  # Detener servidor"
echo ""

# Mostrar información del estudiante
echo "🎓 INFORMACIÓN DEL ESTUDIANTE:"
echo "==============================="
echo "   👤 Nombre: Miguel Villegas Nicholls"
echo "   📚 Curso: Fundamentos de Blockchain"
echo "   📝 Proyecto: Protocolo de Consenso Distribuido"
echo "   📅 Fecha de entrega: $(date +'%d de %B de %Y')"
echo ""

echo "✅ DEMOSTRACIÓN COMPLETA"
echo "🎯 Sistema listo para evaluación del profesor"
echo ""
echo "💡 Para detener el servidor: pkill -f 'uvicorn.*consensus'"
echo "📋 Para revisar logs en tiempo real: tail -f consensus_demo_server.log"
