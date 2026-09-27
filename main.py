"""
AI Intake Cop — Main FastAPI Application
Workshop entrypoint that wires together all lab modules.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from guardrails.router import router as guardrails_router
from triggers.router import router as triggers_router
from background.router import router as background_router
from alerts.router import router as alerts_router
from metrics import metrics_router

app = FastAPI(
    title="AI Intake Cop",
    description="Helicone Analytics & Guardrails Workshop",
    version="1.0.0",
)

# CORS — allows React dashboard on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lab routers
app.include_router(guardrails_router, prefix="/guardrails", tags=["Lab 1 – Guardrails"])
app.include_router(triggers_router,   prefix="/triggers",   tags=["Lab 2 – Triggers"])
app.include_router(background_router, prefix="/tasks",      tags=["Lab 3 – Background Tasks"])
app.include_router(alerts_router,     prefix="/alerts",     tags=["Lab 4 – Budget Alerts"])
app.include_router(metrics_router,    prefix="/metrics-api",tags=["Lab 5/6 – Metrics"])

# Prometheus metrics scrape endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Intake Cop"}


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Intake Cop Workshop!",
        "docs": "/docs",
        "labs": {
            "guardrails": "/guardrails",
            "triggers": "/triggers",
            "background_tasks": "/tasks",
            "budget_alerts": "/alerts",
            "metrics": "/metrics-api",
            "prometheus": "/metrics",
        },
    }
