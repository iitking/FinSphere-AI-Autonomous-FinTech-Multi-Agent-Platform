"""
FinSphere AI - Production Entry Point.
Run:
    python main.py
or:
    uvicorn api.app:app --reload --port 8000
"""

from __future__ import annotations

import uvicorn
from api.app import app
from core.config import settings

if __name__ == "__main__":
    mode_desc = "Offline Simulation Mode (Mock Engine)" if settings.is_simulation_mode else f"Live Anthropic Claude ({settings.model})"
    print("\n" + "=" * 70)
    print(f"🚀  {settings.app_name} v{settings.app_version} Starting...")
    print(f"📡  API Server:        http://{settings.host}:{settings.port}")
    print(f"🖥️   Web Dashboard:     http://localhost:{settings.port}/dashboard")
    print(f"📚  Interactive Docs:  http://localhost:{settings.port}/docs")
    print(f"🧠  Execution Mode:    {mode_desc}")
    print("=" * 70 + "\n")

    uvicorn.run(
        "api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )
