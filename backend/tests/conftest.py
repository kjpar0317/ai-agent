from __future__ import annotations

import os

# Ensure in-memory SQLite before importing the application (engine is created at import time).
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
