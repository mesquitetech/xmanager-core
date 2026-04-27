import sys
import os

# Add backend/ to path so all imports in main.py resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Minimal test to verify the Python runtime works before loading full app
from fastapi import FastAPI as _FastAPI
app = _FastAPI()

@app.get("/api/health")
def health():
    return {"status": "healthy", "mode": "minimal"}

# Load full app — comment out if debugging
try:
    import importlib, types
    _mod = importlib.import_module("main")
    app = _mod.app
except Exception as e:
    # If full import fails, serve a minimal app with the error info
    @app.get("/api/error")
    def error_info():
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
