#!/bin/bash

# Script para ejecutar la dashboard de AMA Bot
echo "🚀 Iniciando AMA Bot Dashboard..."

# Navegar al directorio de la dashboard
cd "$(dirname "$0")"

# Activar entorno virtual
source venv/bin/activate

# Verificar que streamlit esté instalado
if ! command -v streamlit &> /dev/null; then
    echo "📦 Instalando dependencias..."
    pip install streamlit plotly pandas
fi

# Ejecutar la dashboard
echo "📊 Abriendo dashboard en http://localhost:8502"
echo "⏹️  Para detener: Ctrl+C"
echo ""

streamlit run streamlit_dashboard.py --server.port 8502