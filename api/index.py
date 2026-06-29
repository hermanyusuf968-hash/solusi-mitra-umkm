# ============================================================
# api/index.py
# Entry point untuk Vercel Deployment
# Expose FastAPI app sebagai WSGI application
# ============================================================

import os
import sys

# Tambahkan parent directory ke path untuk import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FastAPI app
from backend import app

# Export sebagai default handler untuk Vercel
# Vercel akan mencari 'app' atau 'handler' function
export = app
handler = app
