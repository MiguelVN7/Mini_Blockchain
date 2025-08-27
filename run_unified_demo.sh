#!/bin/bash

# ===========================================================
# Lanzador rápido para la implementación del protocolo de consenso unificado

echo "🎓 Protocolo de Consenso Blockchain - Implementación Unificada"
echo "========================================================================"
echo ""
echo "🚀 Iniciando demostración de consenso unificado..."
echo ""

# Verificar si Python 3 está disponible
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Se requiere Python 3 pero no se encontró"
    echo "Por favor instale Python 3.8+ e intente de nuevo"
    exit 1
fi

# Verificar si los paquetes requeridos están instalados
echo "🔍 Verificando dependencias..."
$PYTHON_CMD -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependencias requeridas..."
    $PYTHON_CMD -m pip install fastapi uvicorn pydantic requests
    if [ $? -ne 0 ]; then
        echo "❌ Falló la instalación de dependencias"
        echo "Por favor ejecute manualmente: pip install fastapi uvicorn pydantic requests"
        exit 1
    fi
fi

echo "✅ Dependencias OK"
echo ""

# Lanzar la implementación unificada
echo "🚀 Iniciando protocolo de consenso unificado..."
echo "   📁 Archivo: blockchain_consensus_unified.py"
echo "   🌐 API estará disponible en: http://localhost:8000"
echo "   📖 Documentación en: http://localhost:8000/docs"
echo ""

$PYTHON_CMD blockchain_consensus_unified.py

echo ""
echo "👋 ¡Demostración de consenso unificado completada!"
echo "📄 Revisar reportes generados para resultados detallados"