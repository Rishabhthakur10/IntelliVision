#!/usr/bin/env bash
# IntelliVision Launcher Script

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate local virtual environment if it exists
if [ -d "$DIR/.venv" ]; then
    source "$DIR/.venv/bin/activate"
fi

if [ "$1" == "landing" ]; then
    echo "🌐 Launching IntelliVision Landing Page on port 5002..."
    python landing_page/app.py
elif [ "$1" == "both" ]; then
    echo "🚀 Launching IntelliVision App and Landing Page..."
    python start.py both
else
    echo "👁️ Launching IntelliVision AI Attendance App on http://localhost:8501 ..."
    streamlit run app.py
fi
