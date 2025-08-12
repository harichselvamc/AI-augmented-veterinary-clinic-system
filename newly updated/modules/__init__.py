# modules/__init__.py
"""Utility to share DB path for all modules."""
from __future__ import annotations
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")
