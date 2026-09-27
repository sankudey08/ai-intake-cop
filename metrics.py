"""
Prometheus metrics definitions and API router for Lab 5/6.
"""
from prometheus_client import Counter, Histogram, Gauge
from fastapi import APIRouter

metrics_router = APIRouter()

# ─── Prometheus metrics ────────────────────────────────────────────────────
INTAKE_REQUESTS = Counter(
    "intake_requests_total",
    "Total intake requests processed",
    ["source", "priority"],
)

GUARDRAIL_BLOCKS = Counter(
    "guardrail_blocks_total",
    "Messages blocked by guardrails",
    ["guardrail_type"],   # regex | semantic
)

LLM_LATENCY = Histogram(
    "llm_response_seconds",
    "Ollama LLM response latency",
    buckets=[0.5, 1, 2, 5, 10, 30],
)

TOKEN_USAGE = Counter(
    "token_usage_total",
    "Total tokens consumed",
    ["model", "type"],    # type: prompt | completion
)

BUDGET_UTILIZATION = Gauge(
    "budget_utilization_pct",
    "Budget utilization percentage (0-100)",
)

ACTIVE_BACKGROUND_TASKS = Gauge(
    "active_background_tasks",
    "Number of currently running background jobs",
)

# ─── API endpoints for React dashboard ────────────────────────────────────

@metrics_router.get("/summary")
async def metrics_summary():
    """
    🔬 LAB 5 — Summary metrics for the React dashboard.
    Returns current Prometheus gauge values and counters as JSON.
    """
    from 04-budget-alerts.router import TOKEN_LEDGER, BUDGET_LIMIT
    from 03-background-tasks.router import JOB_STORE, JOB_LOG

    done = sum(1 for j in JOB_STORE.values() if j["status"] == "done")
    blocked = sum(1 for j in JOB_STORE.values() if j["status"] == "blocked")
    queued = sum(1 for j in JOB_STORE.values() if j["status"] == "queued")

    return {
        "tokens": {
            "used": TOKEN_LEDGER["total_tokens"],
            "limit": BUDGET_LIMIT,
            "utilization_pct": round(TOKEN_LEDGER["total_tokens"] / BUDGET_LIMIT * 100, 1),
        },
        "jobs": {
            "total": len(JOB_STORE),
            "done": done,
            "blocked": blocked,
            "queued": queued,
        },
        "alerts_fired": len(TOKEN_LEDGER["alerts_fired"]),
        "recent_events": list(JOB_LOG)[-10:],
    }
