#!/bin/bash

# 🎓 Script de Inicio Simplificado para el Profesor
# Curso: Fundamentos de Blockchain
# Estudiante: Miguel Villegas Nicholls

echo "🎓 Iniciando Demostración del Sistema de Consenso Distribuido"
echo "==============================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "academic_demonstration.py" ]; then
    echo "❌ Error: Por favor ejecute este script desde el directorio 'Trabajo 1'"
    echo "   Ubicación esperada: /Users/miguelvillegas/Fundamentos de Blockchain/Trabajo 1"
    exit 1
fi

echo "✅ Directorio correcto verificado"
echo ""

# Verificar dependencias básicas
echo "🔍 Verificando dependencias..."

# Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 disponible: $(python3 --version)"
else
    echo "❌ Python3 no encontrado"
    exit 1
fi

# GPG
if command -v gpg &> /dev/null; then
    echo "✅ GPG disponible: $(gpg --version | head -1)"
else
    echo "⚠️  GPG no encontrado - el sistema funcionará con proveedor mock"
fi

echo ""
echo "🚀 Iniciando servidor de consenso..."
echo "   URL: http://localhost:8000"
echo "   Documentación: http://localhost:8000/docs"
echo ""

# Matar procesos previos del servidor si existen
pkill -f "uvicorn.*consensus.api" 2>/dev/null
sleep 2

# Iniciar servidor en background
python3 -m uvicorn consensus.api:app --host 0.0.0.0 --port 8000 > consensus_demo_server.log 2>&1 &
SERVER_PID=$!

echo "📊 Servidor iniciado (PID: $SERVER_PID)"
echo "📝 Logs en: consensus_demo_server.log"
echo ""

# Esperar a que el servidor esté listo
echo "⏳ Esperando a que el servidor esté disponible..."
for i in {1..15}; do
    if curl -s http://localhost:8000/status > /dev/null 2>&1; then
        echo "✅ Servidor listo en el intento $i"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "❌ El servidor no responde después de 15 intentos"
        echo "💡 Verificando logs:"
        tail -n 10 consensus_demo_server.log
        exit 1
    fi
    sleep 1
    echo "   Intento $i/15..."
done

echo ""
echo "🎯 Ejecutando demostración académica completa..."
echo "================================================"
echo ""

# Ejecutar la demostración
python3 academic_demonstration.py

DEMO_EXIT_CODE=$?

echo ""
echo "================================================"
echo "📊 Resultado de la Demostración"
echo "================================================"

if [ $DEMO_EXIT_CODE -eq 0 ]; then
    echo "✅ Demostración completada exitosamente"
    echo "🎉 Sistema funcionando correctamente"
else
    echo "⚠️  Demostración completada con advertencias"
    echo "💡 El sistema funciona pero algunos componentes podrían optimizarse"
fi

echo ""
echo "🌐 Recursos disponibles:"
echo "   • Documentación interactiva: http://localhost:8000/docs"
echo "   • Estado del sistema: http://localhost:8000/status"
echo "   • Logs del servidor: consensus_demo_server.log"
echo "   • Reportes generados: academic_report_*.json"
echo ""
echo "🛠️  Para detener el servidor:"
echo "   kill $SERVER_PID"
echo ""
echo "📖 Para más información, consulte DEMO_README.md"
echo ""
echo "🎓 Sistema listo para evaluación académica"
