# 🧠 AI Intake Cop — Helicone Analytics & Grafana Workshop
**3-Hour Hands-On | Student-Driven | Local Ollama + Docker**

---

## Use Case
**"AI Intake Cop"** — a local-first AI assistant that:
1. Listens to Gmail / Google Calendar for incoming messages and meeting invites
2. Routes each item through an Ollama LLM (local, no API key needed)
3. Enforces content guardrails (regex + semantic filters, red-team drills)
4. Logs every call to Helicone for cost, latency, and safety tracking
5. Fires budget alerts when token spend crosses a threshold
6. Surfaces a live React + Grafana dashboard showing all analytics

---

## Workshop Flow (3 Hours)

| # | Block | Topic | Duration |
|---|-------|-------|----------|
| 1 | 🛡️ Guardrails & Safety | Regex/semantic filters, content policy prompts, red-team drill | 35 min |
| 2 | ⚡ FastAPI Triggers | FastAPI listener endpoints, Gmail/Calendar webhooks | 30 min |
| 3 | 🔄 Background Tasks | FastAPI BackgroundTasks, async job queue | 25 min |
| 4 | 💸 Budget Alerts | Helicone budget hooks, alert thresholds, Slack/email notify | 25 min |
| 5 | 📊 React Dashboard | Live analytics dashboard consuming Helicone API | 30 min |
| 6 | 📈 Grafana | Prometheus scrape, Grafana dashboards, alert rules | 25 min |
| — | 🎯 Capstone | End-to-end live demo & retrospective | 10 min |

---

## Stack
- **LLM**: Ollama (`llama3.2:1b` or `qwen2.5:0.5b`) — runs fully local
- **API**: FastAPI (Python 3.11)
- **Observability**: Helicone (self-hosted or cloud)
- **Metrics**: Prometheus + Grafana
- **Frontend**: React + Vite + Recharts
- **Infra**: Docker Compose (single `docker-compose.yml` boots everything)
- **Triggers**: Gmail API + Google Calendar API (OAuth 2.0)

---

## Quick Start
```bash
git clone <repo>
cd helicone-workshop
cp .env.example .env          # fill in Google OAuth credentials
docker-compose up -d
open http://localhost:5173     # React dashboard
open http://localhost:3000     # Grafana
open http://localhost:8000/docs # FastAPI Swagger
```

---

## Directory Structure
```
helicone-workshop/
├── 01-guardrails/        # Lab 1 — regex filters, semantic guardrails, red-team
├── 02-fastapi-triggers/  # Lab 2 — FastAPI listener, Gmail/Calendar webhooks
├── 03-background-tasks/  # Lab 3 — async background job queue
├── 04-budget-alerts/     # Lab 4 — Helicone budget hooks, alerting
├── 05-react-dashboard/   # Lab 5 — React analytics frontend
├── 06-grafana/           # Lab 6 — Prometheus metrics, Grafana provisioning
├── docker/               # Dockerfiles for each service
├── scripts/              # Helper scripts (seed data, test calls)
├── docs/                 # Architecture diagrams, lab cards
└── docker-compose.yml    # Single-command boot
```
