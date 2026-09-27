# Docker Troubleshooting — Windows
**Read this if `docker compose up -d` fails or a service won't start**

---

## Quick Diagnostics

```bash
docker compose ps                    # Which containers are Up/Exit?
docker compose logs api              # Logs for FastAPI
docker compose logs ollama           # Logs for Ollama
docker compose logs helicone         # Logs for Helicone
docker compose logs grafana          # Logs for Grafana
docker compose logs --tail=50 api    # Last 50 lines only
```

---

## Problem: Docker Desktop won't start

**Symptom:** Whale icon shows "Docker Desktop is starting..." forever.

**Fix 1 — WSL 2 not installed:**
```
Start menu → "Turn Windows features on or off"
Check: ✅ Virtual Machine Platform
Check: ✅ Windows Subsystem for Linux
Restart laptop → re-open Docker Desktop
```

**Fix 2 — Restart Docker service:**
```
Task Manager → Services tab → "com.docker.service" → Restart
```

**Fix 3 — Fully reset Docker:**
```
Docker Desktop → Settings → Troubleshoot → "Reset to factory defaults"
Warning: this deletes all downloaded images. You'll need to re-pull them.
```

---

## Problem: Port already in use

**Symptom:** `Error: bind: address already in use` for port 8000 / 5173 / 3000 / 9090

**Find what's using the port (PowerShell as Admin):**
```powershell
netstat -ano | findstr :8000
# Shows PID. Then:
taskkill /PID <pid> /F
```

**Or change the port in docker-compose.yml:**
```yaml
# Change "8000:8000" to "8001:8000" for the api service
ports:
  - "8001:8000"
# Then access FastAPI at http://localhost:8001/docs
```

---

## Problem: Container exits immediately (Exit 1)

**Symptom:** `docker compose ps` shows a container as `Exit 1` or `Exited`.

**Fix:**
```bash
docker compose logs api      # Read the error — usually a missing .env variable or import error
```

Common causes:
- `.env` file missing → `cp .env.example .env`
- Python import error in your code → fix the syntax error
- Database not ready yet → `docker compose restart api` (give DB 30 seconds to start)

---

## Problem: Ollama model pull is very slow

**The 1.3 GB download is normal on first run.** While it downloads:
- Read Lab 1 in the lab cards
- Set up your `.env` file
- Explore the Swagger UI at http://localhost:8000/docs

If it seems stuck (no progress for 5+ minutes):
```bash
docker exec intake-ollama ollama pull llama3.2:1b
# Watch the progress bar
```

---

## Problem: React dashboard shows blank page

**Fix:**
```bash
docker compose logs dashboard    # Check for npm install errors
docker compose restart dashboard
```
Or open the browser console (F12) and check for CORS or network errors.

Ensure `VITE_API_BASE_URL=http://localhost:8000` is in your `.env`.

---

## Problem: Helicone UI won't load

**Fix:**
```bash
docker compose logs helicone
docker compose logs helicone-db   # Check if Postgres started
docker compose restart helicone
```
Wait 30 seconds after restart, then try http://localhost:8585 again.

---

## Problem: Grafana shows "No data"

This is expected until you send some requests! After completing Lab 1:
1. Run `python scripts/seed_demo_data.py`
2. Refresh Grafana dashboard
3. Set time range to "Last 5 minutes"

If still empty:
```bash
docker compose logs prometheus    # Is it scraping the API?
```
Check http://localhost:9090/targets — the `intake-api` target should be green.

---

## Nuclear Option — Full Reset

If nothing works, this resets everything and starts fresh:
```bash
docker compose down -v            # Stop containers AND delete volumes
docker compose up -d              # Restart fresh
docker exec intake-ollama ollama pull llama3.2:1b   # Re-pull model
```

**Warning:** This deletes all data in Helicone's database. Fine for workshop.

---

## Getting Help

1. Read the error message carefully — it usually tells you exactly what's wrong
2. Search the error on Google (copy the exact error text)
3. Check the workshop Discord/Slack if your trainer set one up
4. Ask the trainer — they've seen this before
