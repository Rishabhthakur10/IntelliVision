#!/usr/bin/env python3
"""
IntelliVision — Attendance System with AI
Launcher script to run the Streamlit App, Landing Page, or Both.
"""
import sys
import subprocess
import os
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "bin", "python")
VENV_STREAMLIT = os.path.join(BASE_DIR, ".venv", "bin", "streamlit")

# Fallback to system python/streamlit if venv not present
PYTHON_EXEC = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
STREAMLIT_EXEC = VENV_STREAMLIT if os.path.exists(VENV_STREAMLIT) else "streamlit"


def run_app():
    print("\n🚀 Starting IntelliVision Streamlit App on http://localhost:8501 ...")
    subprocess.run([STREAMLIT_EXEC, "run", os.path.join(BASE_DIR, "app.py")])


def run_landing():
    print("\n🌐 Starting IntelliVision Landing Page on http://localhost:5002 ...")
    landing_app = os.path.join(BASE_DIR, "landing_page", "app.py")
    subprocess.run([PYTHON_EXEC, landing_app])


def run_both():
    print("\n🌟 Starting both IntelliVision Streamlit App & Landing Page...")
    p1 = subprocess.Popen([STREAMLIT_EXEC, "run", os.path.join(BASE_DIR, "app.py")])
    landing_app = os.path.join(BASE_DIR, "landing_page", "app.py")
    p2 = subprocess.Popen([PYTHON_EXEC, landing_app])

    def shutdown(signum, frame):
        print("\n🛑 Shutting down processes...")
        p1.terminate()
        p2.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    p1.wait()
    p2.wait()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["app", "streamlit"]:
            run_app()
        elif arg in ["landing", "web"]:
            run_landing()
        elif arg in ["both", "all"]:
            run_both()
        else:
            print(f"Usage: python start.py [app | landing | both]")
    else:
        run_app()
