#!/usr/bin/env python3
"""
Script para ejecutar el servidor de consenso de forma simple.
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando servidor de protocolo de consenso...")
    print("📍 API disponible en: http://localhost:8000")
    print("📖 Documentación en: http://localhost:8000/docs")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    uvicorn.run(
        "consensus.api:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False
    )
