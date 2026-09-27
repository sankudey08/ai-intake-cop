"""
LAB 4 — Budget Alerts
Topics: Helicone usage API · token budget tracking · email/log alerts
"""
import os
import time
import httpx
import aiosmtplib
from email.message import EmailMessage
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ─── In-memory token accumulator (Helicone also has native cost limits) ───
TOKEN_LEDGER: dict = {"total_tokens": 0, "sessions": [], "alerts_fired": []}
BUDGET_LIMIT = int(os.getenv("BUDGET_TOKEN_LIMIT", "10000"))


# ─── 4A  Record Token Usage ───────────────────────────────────────────────

class UsageEvent(BaseModel):
    session_id: str
    prompt_tokens: int
    completion_tokens: int
    model: Optional[str] = "llama3.2:1b"

@router.post("/record-usage")
async def record_usage(event: UsageEvent):
    """
    🔬 LAB 4A — Manually record a token usage event.
    In production Helicone captures this automatically via proxy headers.
    """
    total = event.prompt_tokens + event.completion_tokens
    TOKEN_LEDGER["total_tokens"] += total
    TOKEN_LEDGER["sessions"].append({
        "session_id": event.session_id,
        "tokens": total,
        "model": event.model,
        "ts": time.time(),
    })

    over_budget = TOKEN_LEDGER["total_tokens"] >= BUDGET_LIMIT
    if over_budget:
        alert_msg = f"Budget exceeded! {TOKEN_LEDGER['total_tokens']} / {BUDGET_LIMIT} tokens used."
        TOKEN_LEDGER["alerts_fired"].append({"message": alert_msg, "ts": time.time()})
        # Fire async alert — don't await so we don't block the response
        import asyncio
        asyncio.create_task(fire_budget_alert(alert_msg))

    return {
        "recorded_tokens": total,
        "total_tokens": TOKEN_LEDGER["total_tokens"],
        "budget_limit": BUDGET_LIMIT,
        "budget_remaining": max(0, BUDGET_LIMIT - TOKEN_LEDGER["total_tokens"]),
        "over_budget": over_budget,
    }


# ─── 4B  View Budget Status ───────────────────────────────────────────────

@router.get("/status")
async def budget_status():
    """
    🔬 LAB 4B — Check current token budget and alert history.
    """
    used = TOKEN_LEDGER["total_tokens"]
    return {
        "total_tokens_used": used,
        "budget_limit": BUDGET_LIMIT,
        "budget_remaining": max(0, BUDGET_LIMIT - used),
        "utilization_pct": round(used / BUDGET_LIMIT * 100, 1),
        "alerts_fired": len(TOKEN_LEDGER["alerts_fired"]),
        "last_alert": TOKEN_LEDGER["alerts_fired"][-1] if TOKEN_LEDGER["alerts_fired"] else None,
        "recent_sessions": TOKEN_LEDGER["sessions"][-5:],
    }


# ─── 4C  Fire Alert ───────────────────────────────────────────────────────

async def fire_budget_alert(message: str):
    """Send an email alert when budget is exceeded."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    alert_email = os.getenv("BUDGET_ALERT_EMAIL", smtp_user)

    if not smtp_user or not smtp_pass:
        print(f"[ALERT] Email not configured. Alert: {message}")
        return

    msg = EmailMessage()
    msg["Subject"] = "🚨 AI Intake Cop — Budget Alert"
    msg["From"] = smtp_user
    msg["To"] = alert_email
    msg.set_content(f"""Budget alert from AI Intake Cop:

{message}

Check your Helicone dashboard for details.
http://localhost:8585
""")

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            start_tls=True,
        )
        print(f"[ALERT] Email sent to {alert_email}")
    except Exception as e:
        print(f"[ALERT] Email failed: {e}")


@router.post("/test-alert")
async def test_alert():
    """
    🔬 LAB 4C — Manually fire a budget alert to test your SMTP setup.
    """
    await fire_budget_alert("This is a test alert from the workshop!")
    return {"status": "alert_fired", "check": "your email inbox"}


# ─── 4D  Helicone Usage API ───────────────────────────────────────────────

@router.get("/helicone-usage")
async def helicone_usage():
    """
    🔬 LAB 4D — Fetch real usage stats from the Helicone API.
    Requires HELICONE_API_KEY in your .env.
    """
    api_key = os.getenv("HELICONE_API_KEY", "")
    base_url = os.getenv("HELICONE_BASE_URL", "https://api.helicone.ai")

    if not api_key:
        return {"error": "HELICONE_API_KEY not set", "hint": "Add it to your .env file"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{base_url}/v1/request",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"limit": 10, "offset": 0},
            )
            if resp.status_code == 401:
                return {"error": "Invalid Helicone API key"}
            data = resp.json()
            return {"helicone_requests": data}
    except httpx.RequestError as e:
        raise HTTPException(502, f"Helicone API unreachable: {e}")


@router.delete("/reset")
async def reset_budget():
    """Reset the in-memory budget ledger (for demo resets)."""
    TOKEN_LEDGER["total_tokens"] = 0
    TOKEN_LEDGER["sessions"].clear()
    TOKEN_LEDGER["alerts_fired"].clear()
    return {"reset": True, "budget_limit": BUDGET_LIMIT}
