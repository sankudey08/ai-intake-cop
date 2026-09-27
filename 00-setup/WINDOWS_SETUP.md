# Lab 0 — Full Windows Setup Guide
**AI Intake Cop Workshop · Start here if you've never used Git or Docker**

---

## What you'll install in this lab

| Tool | Why |
|------|-----|
| Git for Windows | Version control — clone the workshop repo |
| GitHub account | Host the repo, push your changes |
| Docker Desktop | Runs all services (Ollama, Helicone, Grafana, FastAPI, React) |
| VS Code | Edit code with syntax highlighting |
| Postman (optional) | Alternative to Swagger for testing API endpoints |

Estimated time: **30 minutes** (most of it is download wait time — read ahead while it downloads)

---

## Step 0A — Install Git for Windows

1. Open your browser → go to **https://git-scm.com/download/win**
2. The download starts automatically. Run the installer.
3. Accept all defaults **except** one change:
   - On the "Adjusting your PATH" screen → choose **"Git from the command line and also from 3rd-party software"**
4. Click Next through the rest. Click Install.

**Verify:**
```
Win + R → type cmd → Enter
git --version
```
You should see something like: `git version 2.44.0.windows.1`

---

## Step 0B — Create a GitHub Account

1. Go to **https://github.com** → click **Sign up**
2. Choose a username (e.g. `yourname-aiworkshop`)
3. Verify your email address
4. You're done — stay logged in

---

## Step 0C — Create the Workshop Repository on GitHub

1. On GitHub, click the **+** in the top right → **New repository**
2. Fill in:
   - Repository name: `ai-intake-cop`
   - Description: `AI Intake Cop — Helicone & Grafana Workshop`
   - Visibility: **Public** (so your classmates can see it)
   - ✅ Check **"Add a README file"**
3. Click **Create repository**
4. Copy the repository URL — it looks like:
   `https://github.com/YOUR-USERNAME/ai-intake-cop.git`

---

## Step 0D — Clone the Repository to Your Laptop

Open **Git Bash** (search for it in Start menu) or **Command Prompt**:

```bash
# Go to your Desktop (or wherever you want the project)
cd C:\Users\YOUR-NAME\Desktop

# Clone YOUR repo (replace with your URL)
git clone https://github.com/YOUR-USERNAME/ai-intake-cop.git

# Go into the project folder
cd ai-intake-cop

# Check the status
git status
```

You should see: `nothing to commit, working tree clean`

---

## Step 0E — Copy the Workshop Starter Files

 The starter code as a ZIP or via a shared GitHub link.

**shares a ZIP:**
```
1. Extract the ZIP to your Desktop
2. Copy all files from the extracted folder into ai-intake-cop\
3. Do NOT overwrite the .git folder
```

After, verify:
```bash
ls          # (Git Bash) or dir (Command Prompt)
# You should see: main.py  requirements.txt  docker-compose.yml  01-guardrails/  etc.
```

---

## Step 0F — Your First Git Commit

```bash
# Tell Git who you are (one-time setup)
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Stage all files
git add .

# Commit
git commit -m "Initial workshop setup"

# Push to GitHub
git push origin main
```

Open GitHub in your browser — refresh the page. You should see your files there. ✅

---

## Step 0G — Install Docker Desktop

1. Go to **https://www.docker.com/products/docker-desktop**
2. Click **"Download for Windows"**
3. Run the installer. **Requires Windows 10/11 with WSL 2.**
   - If asked to install WSL 2: click Yes and let it install.
   - Restart your laptop when prompted.
4. Open Docker Desktop from the Start menu.
5. Wait for the whale icon in the taskbar to show a green "Running" state.

**Verify:**
```bash
docker --version
docker compose version
```
Expected: `Docker version 26.x.x` and `Docker Compose version v2.x.x`

**WSL 2 troubleshooting (if Docker won't start):**
```
Start menu → "Turn Windows features on or off"
✅ Virtual Machine Platform
✅ Windows Subsystem for Linux
Restart → re-open Docker Desktop
```

---

## Step 0H — Set Up the .env File

```bash
# In the ai-intake-cop folder:
copy .env.example .env         # Windows Command Prompt
# OR
cp .env.example .env           # Git Bash
```

Open `.env` in VS Code (or Notepad):
```
code .env
```

For now, leave everything as-is. You'll fill in Google credentials in Lab 2 and email settings in Lab 4.

---

## Step 0I — Start All Services with Docker Compose

```bash
docker compose up -d
```
```
What docker compose up -d does

docker compose reads your docker-compose.yml file and manages multiple containers as one unit.

up — create and start all the services defined in the file
-d — "detached" mode, meaning containers run in the background (your terminal is free)
```
First run downloads ~4 GB of images. **This takes 5–15 minutes on a fresh laptop.** While it downloads, read ahead in the lab cards.

Watch the progress:
```bash
docker compose logs -f
```
Press `Ctrl+C` to stop watching logs (services keep running).

**Verify all containers are running:**
```bash
docker compose ps
```
You should see 7 services all with status `Up`.

---

## Step 0J — Pull the Ollama Model

```bash
# This downloads the local LLM (~1.3 GB)
docker exec intake-ollama ollama pull llama3.2:1b
```

Wait for: `success` — the model is ready.

Test it:
```bash
docker exec intake-ollama ollama run llama3.2:1b "Say hello in one sentence"
```

---

## Step 0K — Verify All Service URLs

Open these in your browser — all should load:

| URL | What you see |
|-----|-------------|
| http://localhost:8000/docs | FastAPI Swagger UI — workshop API |
| http://localhost:8000/health | `{"status":"ok"}` |
| http://localhost:5173 | React Analytics Dashboard |
| http://localhost:3000 | Grafana (login: admin / admin123) |
| http://localhost:9090 | Prometheus targets |
| http://localhost:8585 | Helicone self-hosted UI |

If any URL doesn't load, check:
```bash
docker compose ps          # is the container "Up"?
docker compose logs api    # check the FastAPI container for errors
```

---

## Step 0L — Set Up Helicone (Self-Hosted)

Helicone started automatically with Docker Compose. Let's configure it:

1. Open **http://localhost:8585**
2. Click **"Get Started"** or **"Sign Up"**
3. Create a local account (any email/password — this is local only)
4. Once logged in → go to **Settings → API Keys**
5. Click **"Create API Key"** → copy the key
6. Open your `.env` file and paste it:
   ```
   HELICONE_API_KEY=sk-helicone-xxxxxxxxxxxx
   HELICONE_BASE_URL=http://localhost:8585/v1
   ```
7. Restart the API container to pick up the new key:
   ```bash
   docker compose restart api
   ```

**Verify:** Go to http://localhost:8585 → you should see a Requests dashboard (empty for now — calls will appear after Lab 1).

---

## Step 0M — Set Up Grafana

Grafana started automatically and the dashboard is pre-provisioned. Let's verify:

1. Open **http://localhost:3000**
2. Login: **admin** / **admin123**
3. Click **Skip** if it asks you to change password (for workshop)
4. Left sidebar → **Dashboards** → **Workshop** folder
5. Open **"AI Intake Cop — Analytics"**

You should see 9 empty panels. They'll fill with data once you start sending requests in Lab 1.

**Quick exploration (2 min):**
- Click any panel → **Edit** → look at the Prometheus query
- Notice `intake_requests_total`, `llm_response_seconds`, `budget_utilization_pct`
- You'll build a new panel yourself in Lab 6

---

## Step 0N — Set Up Gmail & Google Calendar (for Lab 2 Demo)

This sets up the Google Cloud project that lets the AI Intake Cop receive real emails and calendar events.

### 0N-1: Create a Google Cloud Project
1. Go to **https://console.cloud.google.com**
2. Click the project dropdown (top left) → **"New Project"**
3. Name: `ai-intake-cop-workshop` → **Create**
4. Select the new project from the dropdown

### 0N-2: Enable Required APIs
1. Left menu → **"APIs & Services"** → **"Enable APIs and Services"**
2. Search for and enable each of these (click Enable on each):
   - **Gmail API**
   - **Google Calendar API**
   - **Cloud Pub/Sub API** (needed for Gmail push notifications)
3. You should see all 3 in your **Enabled APIs** list

### 0N-3: Create OAuth 2.0 Credentials
1. Left menu → **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. If prompted to configure consent screen first:
   - User Type: **External** → Create
   - App name: `AI Intake Cop`
   - User support email: your email
   - Developer contact: your email
   - Click **Save and Continue** through all steps
   - Click **Back to Dashboard**
4. Back on Credentials → **"+ Create Credentials"** → **"OAuth client ID"**
5. Application type: **Web application**
6. Name: `AI Intake Cop Workshop`
7. Under **"Authorized redirect URIs"** → click **"+ Add URI"**:
   ```
   http://localhost:8000/triggers/auth/callback
   ```
8. Click **Create**
9. A popup shows your **Client ID** and **Client Secret** — copy both

### 0N-4: Add Credentials to .env
Open `.env` in VS Code:
```
GOOGLE_CLIENT_ID=your-client-id-from-step-above.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/triggers/auth/callback
```

### 0N-5: Add Yourself as a Test User
1. Left menu → **"APIs & Services"** → **"OAuth consent screen"**
2. Scroll to **"Test users"** → click **"+ Add Users"**
3. Add your Gmail address → **Save**

### 0N-6: Restart and Authorize
```bash
docker compose restart api
```

Then in your browser:
```
http://localhost:8000/triggers/auth/url
```
Copy the `auth_url` from the response → paste it in a new browser tab → sign in with your Google account → grant permissions.

You'll be redirected to `/triggers/auth/callback` — you should see:
```json
{"message": "Tokens received!", "access_token": "ya29...", "refresh_token": "PRESENT"}
```

✅ **Gmail and Calendar are now authorized.**

---

## Step 0O — Commit Your Setup

```bash
# In your ai-intake-cop folder
git add .env.example          # commit the template (NOT .env — never commit secrets!)
git status                    # .env should NOT be listed (it's in .gitignore)
git commit -m "Lab 0 complete: Docker, Helicone, Grafana all running"
git push origin main
```

Check GitHub — your commit is there. ✅

---

## ✅ Lab 0 Complete — All Checkpoints

- [ ] `git --version` shows a version number
- [ ] GitHub repo created and files pushed
- [ ] `docker compose ps` shows 7 containers Up
- [ ] `ollama run llama3.2:1b` responds
- [ ] http://localhost:8000/docs loads Swagger
- [ ] http://localhost:5173 loads React Dashboard
- [ ] http://localhost:3000 loads Grafana with the pre-built dashboard
- [ ] http://localhost:8585 loads Helicone with your API key set
- [ ] Helicone API key is in `.env` and API restarted
- [ ] Google OAuth credentials in `.env` (if doing Lab 2 with live Gmail)

**If any checkbox is red, stop and ask the trainer before moving to Lab 1.**
