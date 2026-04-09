"""Ponto de entrada WSGI para o Vercel (Serverless)."""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app import app  # noqa: E402
