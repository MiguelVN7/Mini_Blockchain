#!/bin/bash

# 🚀 Script de Ejecución Simple - Sistema de Consenso Simplificado
# Autor: Miguel Villegas Nicholls
# Curso: Fundamentos de Blockchain

echo "🎓 Sistema de Consenso Distribuido Simplificado"
echo "=============================================="
echo "Estudiante: Miguel Villegas Nicholls"
echo "Fecha: $(date '+%d de %B de %Y')"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "consensus_system.py" ]; then
    echo "❌ Error: Ejecute este script desde el directorio que contiene consensus_system.py"
    exit 1
fi

echo "✅ Archivos del sistema encontrados"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instale Python 3.8+ para continuar."
    exit 1
fi

echo "✅ Python3 disponible: $(python3 --version)"

# Verificar dependencias críticas
echo ""
echo "🔍 Verificando dependencias..."

MISSING_DEPS=0

# Verificar FastAPI
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI no encontrado"
    MISSING_DEPS=1
else
    echo "✅ FastAPI disponible"
fi

# Verificar Uvicorn
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "❌ Uvicorn no encontrado"
    MISSING_DEPS=1
else
    echo "✅ Uvicorn disponible"
fi

# Verificar Pydantic
if ! python3 -c "import pydantic" 2>/dev/null; then
    echo "❌ Pydantic no encontrado"
    MISSING_DEPS=1
else
    echo "✅ Pydantic disponible"
fi

# Verificar Requests
if ! python3 -c "import requests" 2>/dev/null; then
    echo "❌ Requests no encontrado"
    MISSING_DEPS=1
else
    echo "✅ Requests disponible"
fi

# Si faltan dependencias, ofrecer instalarlas
if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "⚠️ Faltan dependencias críticas."
    echo "¿Desea instalar las dependencias automáticamente? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy] ]]; then
        echo "📦 Instalando dependencias..."
        pip3 install fastapi uvicorn pydantic requests
        
        if [ $? -eq 0 ]; then
            echo "✅ Dependencias instaladas correctamente"
        else
            echo "❌ Error instalando dependencias. Instálelas manualmente:"
            echo "   pip3 install fastapi uvicorn pydantic requests"
            exit 1
        fi
    else
        echo "❌ No se puede continuar sin las dependencias."
        echo "Instálelas con: pip3 install fastapi uvicorn pydantic requests"
        exit 1
    fi
fi

echo ""
echo "🎯 Seleccione el modo de ejecución:"
echo "1. 🎯 Demostración automática completa (Recomendado)"
echo "2. 🌐 Solo servidor de consenso"
echo "3. 🔗 Blockchain con consenso integrado"
echo ""

read -p "Seleccione una opción (1-3): " opcion

case $opcion in
    1)
        echo ""
        echo "🚀 Ejecutando demostración automática completa..."
        echo "   Este modo ejecutará todas las pruebas automáticamente"
        echo "   y generará un reporte completo del sistema."
        echo ""
        python3 demo_complete.py
        ;;
    2)
        echo ""
        echo "🌐 Iniciando servidor de consenso..."
        echo "   URL: http://localhost:8000"
        echo "   Documentación: http://localhost:8000/docs"
        echo "   Presione Ctrl+C para detener"
        echo ""
        python3 consensus_system.py
        ;;
    3)
        echo ""
        echo "🔗 Iniciando blockchain con consenso integrado..."
        echo "   Este modo incluye tanto el blockchain como el consenso"
        echo "   en un sistema unificado con interfaz interactiva."
        echo ""
        if [ -f "blockchain_with_consensus.py" ]; then
            python3 blockchain_with_consensus.py
        else
            echo "❌ blockchain_with_consensus.py no encontrado"
            echo "Ejecutando solo el servidor de consenso..."
            python3 consensus_system.py
        fi
        ;;
    *)
        echo "❌ Opción inválida. Ejecutando demostración automática..."
        python3 demo_complete.py
        ;;
esac

echo ""
echo "✅ Ejecución completada."
echo ""
echo "📚 Recursos adicionales:"
echo "   • README_SIMPLE.md - Documentación completa"
echo "   • consensus_system.py - Código fuente principal" 
echo "   • Reportes JSON - Resultados de ejecución"
echo ""
echo "🎓 Sistema listo para evaluación académica"
