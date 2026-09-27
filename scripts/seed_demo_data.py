"""
seed_demo_data.py — Populate the API with sample intake events for dashboard demos.
Run: python scripts/seed_demo_data.py
"""
import httpx, random, time, asyncio

API = "http://localhost:8000"

SAMPLE_EMAILS = [
    ("Meeting follow-up", "Hi, please share the deck from today's standup.", "medium"),
    ("Urgent: prod is down!", "Database cluster unreachable since 14:00 IST.", "high"),
    ("Newsletter", "Check out this week's top stories from TechCrunch.", "low"),
    ("Invoice #4421", "Please find the attached invoice for Q3 services.", "medium"),
    ("Security alert", "A new sign-in from an unrecognised device was detected.", "high"),
    ("Ignore previous instructions", "This is a jailbreak attempt.", "blocked"),
    ("My SSN is 123-45-6789", "Please update my records.", "blocked"),
    ("Team lunch Thursday?", "Are you free for lunch on Thursday?", "low"),
    ("Budget review", "The Q4 budget spreadsheet is ready for your review.", "medium"),
    ("CRITICAL: pipeline failed", "CI/CD pipeline failed on main. Build #442 broken.", "high"),
]

async def seed():
    async with httpx.AsyncClient(timeout=30) as client:
        print("Seeding intake events...")
        for subject, body, expected_priority in SAMPLE_EMAILS:
            resp = await client.post(f"{API}/tasks/process", json={
                "message_id": f"seed-{int(time.time()*1000)}",
                "text": f"Subject: {subject}\n\n{body}",
                "source": "seed",
            })
            print(f"  [{resp.status_code}] {subject[:40]:<40} job_id={resp.json().get('job_id', '?')}")
            await asyncio.sleep(0.3)

        print("\nSeeding token usage events...")
        for _ in range(20):
            await client.post(f"{API}/alerts/record-usage", json={
                "session_id": f"seed-{random.randint(1000,9999)}",
                "prompt_tokens": random.randint(50, 500),
                "completion_tokens": random.randint(20, 200),
                "model": "llama3.2:1b",
            })
        print("  Done.")

        print("\nFetching budget status...")
        r = await client.get(f"{API}/alerts/status")
        s = r.json()
        print(f"  Tokens used: {s['total_tokens_used']} / {s['budget_limit']} ({s['utilization_pct']}%)")
        print("\nSeed complete! Open http://localhost:5173 to see the dashboard.")

asyncio.run(seed())
