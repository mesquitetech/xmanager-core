import sys
import os
import traceback

# Add backend/ to path so all imports in main.py resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

try:
    from main import app
except Exception as _import_error:
    # Expose the import error as a minimal ASGI app for debugging
    _tb = traceback.format_exc()

    async def app(scope, receive, send):
        if scope["type"] == "http":
            body = f"Import error:\n{_tb}".encode()
            await send({"type": "http.response.start", "status": 500,
                        "headers": [[b"content-type", b"text/plain"]]})
            await send({"type": "http.response.body", "body": body})
