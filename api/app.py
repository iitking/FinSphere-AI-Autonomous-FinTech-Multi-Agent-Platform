"""
FastAPI Application Entry Point.
Configures middleware, orchestrator lifecycle, static dashboard assets,
and registers all FinTech agent routing modules.
"""

from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from agents.orchestrator import Orchestrator
from api.routes.analysis import router as analysis_router
from api.routes.compliance import router as compliance_router
from api.routes.config_routes import router as config_router
from api.routes.fraud import router as fraud_router
from api.routes.orchestrator import router as orchestrator_router
from api.routes.portfolio import router as portfolio_router
from api.routes.risk import router as risk_router
from core.config import settings
from core.logging import get_logger, setup_logging

setup_logging()
log = get_logger("app")

app = FastAPI(
    title=settings.app_name,
    description=(
        "Next-Generation Autonomous Multi-Agent Financial Intelligence Platform. "
        "Engineered for Indian FinTechs & Global Markets with Enterprise Guardrails, "
        "Dynamic Risk Weighting, and Statutory Compliance."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate core orchestrator engine
orchestrator = Orchestrator()
app.state.orchestrator = orchestrator

# Mount Static UI Files if available
UI_DIR = Path(__file__).resolve().parent.parent / "ui"
if UI_DIR.exists() and (UI_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")

# Register API Router Modules
app.include_router(orchestrator_router, prefix="/api/v1/query",      tags=["1. Autonomous Orchestrator"])
app.include_router(analysis_router,     prefix="/api/v1/analysis",   tags=["2. Financial Analysis"])
app.include_router(risk_router,         prefix="/api/v1/risk",       tags=["3. Risk Assessment"])
app.include_router(portfolio_router,    prefix="/api/v1/portfolio",  tags=["4. Portfolio Optimization"])
app.include_router(fraud_router,        prefix="/api/v1/fraud",      tags=["5. Fraud Detection"])
app.include_router(compliance_router,   prefix="/api/v1/compliance", tags=["6. Regulatory Compliance"])
app.include_router(config_router,       prefix="/api/v1/config",     tags=["7. System Configuration & Parameters"])


@app.get("/health", tags=["Health & Status"])
async def health():
    """Liveness probe and system status check."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "simulation_mode": settings.is_simulation_mode,
        "active_model": settings.model,
    }


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def root():
    """Serves the interactive multi-agent dashboard or redirects to docs."""
    index_file = UI_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h2>FinSphere AI Multi-Agent System</h2><p>Visit <a href='/docs'>/docs</a> for the API.</p>")


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard():
    """Direct route to the UI Dashboard."""
    index_file = UI_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h2>FinSphere AI Multi-Agent System</h2><p>Visit <a href='/docs'>/docs</a> for the API.</p>")
