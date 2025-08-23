#!/usr/bin/env python3
"""
Script para ejecutar el servidor de consenso.
"""

import sys
import os

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import uvicorn
    from consensus.api import app
    
    print("🚀 Iniciando servidor de protocolo de consenso...")
    print("📍 API disponible en: http://localhost:8000")
    print("📖 Documentación en: http://localhost:8000/docs")
    print("🔍 Estado del consenso: http://localhost:8000/status")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        reload_dirs=["consensus"]
    )
