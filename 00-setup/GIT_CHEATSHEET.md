# Git Cheatsheet for This Workshop
**Keep this open in a tab throughout the session**

---

## The 3 Commands You'll Use Most

```bash
git add .                          # Stage all changed files
git commit -m "your message here"  # Save a snapshot
git push origin main               # Upload to GitHub
```

## Check What's Changed

```bash
git status                  # What files have changed?
git diff                    # What exactly changed in those files?
git log --oneline           # Show recent commits
```

## Undo Mistakes

```bash
git restore filename.py     # Throw away unsaved changes in ONE file
git restore .               # Throw away ALL unsaved changes (careful!)
git stash                   # Temporarily hide changes to try something else
git stash pop               # Bring hidden changes back
```

## Branches (for the adventurous)

```bash
git checkout -b feature/my-guardrail    # Create + switch to new branch
git checkout main                        # Switch back to main
git merge feature/my-guardrail           # Merge your branch into main
```

## Workshop Git Habit

After completing each lab checkpoint:
```bash
git add .
git commit -m "Lab 1 complete: regex + semantic guardrails"
git push origin main
```

This gives you a checkpoint to roll back to if something breaks in the next lab.

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `fatal: not a git repository` | You're in the wrong folder. `cd ai-intake-cop` |
| `error: failed to push — rejected` | Someone else pushed first: `git pull --rebase origin main` then push again |
| `Please tell me who you are` | Run `git config --global user.name "Name"` and `git config --global user.email "email"` |
| `Untracked files: .env` | Good — never `git add .env`. It's in `.gitignore` by design. |
| `nothing to commit` | You're already up to date — nothing to do |

---

## Lab Commit Messages (copy-paste ready)

```
Lab 0 complete: Docker, Helicone, Grafana all running
Lab 1A: regex guardrail — DROP TABLE pattern added
Lab 1B: semantic classifier confirmed working
Lab 1C: red-team drill complete
Lab 2A: manual intake endpoint tested
Lab 2B: Gmail webhook — base64 decode working
Lab 2C: Calendar webhook handler confirmed
Lab 3A: background task enqueue and poll working
Lab 3B: batch fan-out — 5 messages, 1 blocked
Lab 4A: budget alert fires at 10000 tokens
Lab 4C: test email alert confirmed
Lab 5C: blocked-jobs stat card added to dashboard
Lab 6C: active-tasks gauge panel added to Grafana
```

---

## What NEVER Goes in Git

- `.env` file (has your passwords and API keys)
- `node_modules/` folder (too big, auto-reinstalled)
- `__pycache__/` (Python bytecode — auto-generated)

The `.gitignore` file already protects you from these.
