#!/bin/bash

# Academic Blockchain Consensus - Unified Demo Launcher
# =====================================================
# Quick launcher for the unified consensus protocol implementation
# Author: Miguel Villegas Nicholls (Optimized)

echo "🎓 Academic Blockchain Consensus Protocol - Unified Implementation"
echo "=================================================================="
echo ""
echo "🚀 Launching unified consensus demonstration..."
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python 3 is required but not found"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
$PYTHON_CMD -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required dependencies..."
    $PYTHON_CMD -m pip install fastapi uvicorn pydantic requests
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        echo "Please run manually: pip install fastapi uvicorn pydantic requests"
        exit 1
    fi
fi

echo "✅ Dependencies OK"
echo ""

# Launch the unified implementation
echo "🚀 Starting unified consensus protocol..."
echo "   📁 File: blockchain_consensus_unified.py"
echo "   🌐 API will be available at: http://localhost:8000"
echo "   📖 Documentation at: http://localhost:8000/docs"
echo ""

$PYTHON_CMD blockchain_consensus_unified.py

echo ""
echo "👋 Unified consensus demonstration completed!"
echo "📄 Check generated reports for detailed results"