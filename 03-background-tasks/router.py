"""
LAB 3 — Background Tasks
Topics: FastAPI BackgroundTasks · async job queue · Redis task log
"""
import asyncio
import os
import time
import uuid
from collections import deque
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import httpx

router = APIRouter()

# ─── In-memory job store (replace with Redis in production) ───────────────
JOB_STORE: dict[str, dict] = {}
JOB_LOG: deque = deque(maxlen=100)   # circular buffer of last 100 events


# ─── 3A  Simple BackgroundTasks Demo ──────────────────────────────────────

class ProcessRequest(BaseModel):
    message_id: str
    text: str
    source: Optional[str] = "manual"

async def run_intake_pipeline(job_id: str, text: str, source: str):
    """
    The actual background pipeline:
    1. Regex guardrail check
    2. LLM triage via Ollama
    3. Log to Helicone (via headers)
    """
    import re, json as _json

    JOB_STORE[job_id]["status"] = "running"
    JOB_STORE[job_id]["started_at"] = time.time()
    JOB_LOG.append({"job_id": job_id, "event": "started", "ts": time.time()})

    # Step 1: Regex guardrail
    blocked = bool(re.search(r"\b(password|secret|ssn)\b", text, re.IGNORECASE))
    if blocked:
        JOB_STORE[job_id]["status"] = "blocked"
        JOB_STORE[job_id]["result"] = {"reason": "regex_guardrail", "safe": False}
        JOB_LOG.append({"job_id": job_id, "event": "blocked_by_regex", "ts": time.time()})
        return

    # Step 2: Simulate LLM call (real call adds ~2-5s)
    await asyncio.sleep(0.5)   # remove this in lab — replace with real Ollama call

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    prompt = f"Classify priority of this intake message in one word (HIGH/MEDIUM/LOW): {text[:200]}"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            llm_reply = resp.json().get("message", {}).get("content", "MEDIUM").strip()
    except Exception as e:
        llm_reply = f"LLM_ERROR: {e}"

    JOB_STORE[job_id]["status"] = "done"
    JOB_STORE[job_id]["result"] = {
        "priority": llm_reply,
        "source": source,
        "duration_s": round(time.time() - JOB_STORE[job_id]["started_at"], 2),
    }
    JOB_LOG.append({"job_id": job_id, "event": "completed", "priority": llm_reply, "ts": time.time()})


@router.post("/process")
async def enqueue_task(req: ProcessRequest, background_tasks: BackgroundTasks):
    """
    🔬 LAB 3A — Enqueue a message for async background processing.
    Returns immediately with a job_id. Poll /tasks/status/{job_id} for result.
    """
    job_id = str(uuid.uuid4())[:8]
    JOB_STORE[job_id] = {
        "job_id": job_id,
        "message_id": req.message_id,
        "status": "queued",
        "queued_at": time.time(),
    }
    background_tasks.add_task(run_intake_pipeline, job_id, req.text, req.source)
    return {"job_id": job_id, "status": "queued", "poll": f"/tasks/status/{job_id}"}


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    🔬 LAB 3B — Poll job status.
    Status lifecycle: queued → running → done | blocked | error
    """
    job = JOB_STORE.get(job_id)
    if not job:
        return {"error": "job_id not found"}
    return job


@router.get("/log")
async def get_job_log():
    """
    🔬 LAB 3C — View the circular buffer of recent background task events.
    """
    return {"events": list(JOB_LOG), "total_in_store": len(JOB_STORE)}


@router.delete("/log")
async def clear_job_log():
    """Clear the job log and store (for demo resets)."""
    JOB_STORE.clear()
    JOB_LOG.clear()
    return {"cleared": True}


# ─── 3D  Batch Processing Demo ────────────────────────────────────────────

class BatchRequest(BaseModel):
    messages: list[str]

@router.post("/batch")
async def batch_process(req: BatchRequest, background_tasks: BackgroundTasks):
    """
    🔬 LAB 3D — Enqueue multiple messages in one call.
    Demonstrates fan-out background tasks.
    """
    job_ids = []
    for i, text in enumerate(req.messages[:10]):   # cap at 10
        job_id = str(uuid.uuid4())[:8]
        JOB_STORE[job_id] = {"job_id": job_id, "status": "queued", "index": i, "queued_at": time.time()}
        background_tasks.add_task(run_intake_pipeline, job_id, text, "batch")
        job_ids.append(job_id)

    return {"enqueued": len(job_ids), "job_ids": job_ids}
