import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI as _FastAPI

# Always define app at module level so Vercel static analysis finds it
app = _FastAPI()
_import_error = None
_import_tb = None

try:
    import main as _main
    app = _main.app
except Exception as _e:
    _import_error = str(_e)
    _import_tb = traceback.format_exc()

    @app.get("/api/health")
    def health():
        return {"status": "import_failed", "error": _import_error, "traceback": _import_tb}
