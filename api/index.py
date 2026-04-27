import sys
import os

# Add backend/ to path so all imports in main.py resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app
