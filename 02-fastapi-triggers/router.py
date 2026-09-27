"""
LAB 2 — FastAPI Triggers
Topics: FastAPI listener endpoints · Gmail webhook · Calendar webhook
"""
import os
import base64
import json
import httpx
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ─── 2A  Manual Intake Trigger ────────────────────────────────────────────

class IntakeRequest(BaseModel):
    source: str           # "gmail" | "calendar" | "manual"
    subject: str
    body: str
    sender: Optional[str] = None

async def call_ollama(prompt: str, model: str = None) -> str:
    """Send a prompt to local Ollama and return the text response."""
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")

@router.post("/intake")
async def manual_intake(req: IntakeRequest):
    """
    🔬 LAB 2A — Manually trigger the AI Intake Cop with any message.
    Simulates what Gmail/Calendar webhooks do automatically.
    """
    prompt = f"""You are an AI email intake assistant. Triage the following message:

Subject: {req.subject}
From: {req.sender or 'unknown'}
Source: {req.source}

Body:
{req.body}

Reply with JSON: {{"priority": "HIGH|MEDIUM|LOW", "action": "<one line>", "summary": "<two sentences>"}}"""

    try:
        result_text = await call_ollama(prompt)
        try:
            result = json.loads(result_text)
        except Exception:
            result = {"raw": result_text}
        return {"source": req.source, "subject": req.subject, "triage": result}
    except Exception as e:
        raise HTTPException(502, f"LLM call failed: {e}")


# ─── 2B  Gmail Push Webhook ────────────────────────────────────────────────

@router.post("/gmail/webhook")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    🔬 LAB 2B — Gmail Pub/Sub push notification receiver.
    Google sends a base64-encoded message envelope here.
    Set this as your Gmail watch() pushEndpoint.
    """
    body = await request.json()
    # Gmail wraps the message in a Pub/Sub envelope
    pubsub_message = body.get("message", {})
    encoded_data = pubsub_message.get("data", "")

    if not encoded_data:
        raise HTTPException(400, "No Pub/Sub data in payload")

    try:
        decoded = base64.b64decode(encoded_data).decode("utf-8")
        message_data = json.loads(decoded)
    except Exception as e:
        raise HTTPException(400, f"Could not decode Pub/Sub message: {e}")

    email_address = message_data.get("emailAddress", "unknown")
    history_id = message_data.get("historyId", "unknown")

    # Queue async processing — don't block the webhook response
    background_tasks.add_task(process_gmail_notification, email_address, history_id)

    # Google requires HTTP 200 within 10 seconds or it retries
    return {"status": "accepted", "historyId": history_id}


async def process_gmail_notification(email_address: str, history_id: str):
    """Background job: fetch the email from Gmail API and run through intake."""
    print(f"[Gmail] Processing notification for {email_address}, historyId={history_id}")
    # In a real implementation: fetch email via Gmail API, then call /intake
    # For the workshop, students fill this in during Lab 3.
    pass


# ─── 2C  Calendar Webhook ─────────────────────────────────────────────────

@router.post("/calendar/webhook")
async def calendar_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    🔬 LAB 2C — Google Calendar push notification receiver.
    Set this as your Calendar watch() address.
    Headers contain X-Goog-Channel-ID, X-Goog-Resource-State.
    """
    channel_id = request.headers.get("X-Goog-Channel-ID", "unknown")
    resource_state = request.headers.get("X-Goog-Resource-State", "unknown")
    resource_id = request.headers.get("X-Goog-Resource-ID", "unknown")

    print(f"[Calendar] channel={channel_id} state={resource_state} resource={resource_id}")

    if resource_state == "sync":
        # Google sends a sync message on first registration — acknowledge only
        return {"status": "sync_ack"}

    background_tasks.add_task(process_calendar_event, channel_id, resource_id)
    return {"status": "accepted", "channel": channel_id}


async def process_calendar_event(channel_id: str, resource_id: str):
    """Background job: fetch the changed event and run through intake."""
    print(f"[Calendar] Processing event resource={resource_id}")
    # Students fill in: call Google Calendar API → /intake
    pass


# ─── 2D  OAuth Setup Helpers ──────────────────────────────────────────────

@router.get("/auth/url")
async def get_auth_url():
    """
    🔬 LAB 2D — Returns the Google OAuth URL students paste into their browser.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/triggers/auth/callback")
    scopes = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/calendar.readonly"

    if not client_id:
        return {"error": "GOOGLE_CLIENT_ID not set in .env"}

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        f"&scope={scopes.replace(' ', '%20')}"
        "&access_type=offline"
        "&prompt=consent"
    )
    return {"auth_url": url}


@router.get("/auth/callback")
async def auth_callback(code: str, state: Optional[str] = None):
    """
    🔬 LAB 2D — OAuth callback. Exchange code for tokens.
    Google redirects here after the user grants permission.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/triggers/auth/callback")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        tokens = resp.json()

    # In production store tokens securely. Workshop: return for inspection.
    return {
        "message": "Tokens received! Store access_token and refresh_token.",
        "access_token": tokens.get("access_token", "")[:20] + "...",
        "refresh_token": tokens.get("refresh_token", "PRESENT" if "refresh_token" in tokens else "MISSING"),
        "expires_in": tokens.get("expires_in"),
    }
