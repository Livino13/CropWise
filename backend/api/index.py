"""Vercel ASGI entrypoint for the CropWise FastAPI app.

Vercel's Python runtime looks for an ASGI/WSGI ``app`` inside ``api/``.
The real application lives in ``backend/app``, so we add the project root
to ``sys.path`` before importing it.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402,F401
