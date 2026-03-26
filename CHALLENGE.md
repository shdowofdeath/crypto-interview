# CryptoWatch — Engineering Interview Challenge

Welcome. This is a real codebase, not a toy exercise.

**Your job: make it work.**

---

## What Is This

CryptoWatch is a live cryptocurrency price dashboard with portfolio tracking.

- **Backend:** FastAPI (Python) — fetches live prices from CoinGecko
- **Frontend:** React + Vite (TypeScript) — displays prices and portfolio value

Right now, it has **8 bugs**. Some are subtle. Some are security issues.
Some will only appear under load or with real data. Find them, fix them, explain
your reasoning.

---

## Getting Started

This repo is configured for **CodeSandbox** — it starts automatically.

If running locally:

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Your Task

### 1. Find and fix all 8 bugs

The bugs are spread across backend and frontend. They range from a crash on
every real API call, to a Python async antipattern, to a React closure bug,
to a security misconfiguration.

All bugs are in application code — not in config files or build tooling.

**Fix root causes, not symptoms. The app must work end-to-end after your fixes.**

### 2. Open a pull request

Create a branch from `main`, commit your fixes, open a PR.

The PR description is part of the assessment. It must include:

- Each bug you found: **file, line, root cause**
- How you fixed it and why
- Any concerns about the codebase you'd raise in a real code review
- Anything you'd do differently if building this from scratch

---

## Hints

You won't catch all 8 from a quick scan. Some require:

- Reading the CoinGecko API docs to know what fields the response actually returns
- Understanding how Python's asyncio event loop handles blocking I/O
- Knowing the CORS spec well enough to spot the security antipattern
- Understanding React's closure semantics in `useEffect`

If you find fewer than 8, keep looking. If you find more, tell us.

---

## Evaluation

| Area | What We Look For |
|---|---|
| Bug identification | Did you find all 8? Do you understand each root cause? |
| Code quality | Are fixes idiomatic and production-appropriate? |
| Security awareness | Did you identify and explain the CORS issue? |
| Async understanding | Did you fix the blocking I/O correctly, not just swap libraries? |
| Communication | Is your PR description clear, specific, and professional? |

---

## Rules

- Do not add dependencies without justification
- Do not refactor unrelated code
- Do not use explanations you can't defend — we will ask follow-up questions on every fix in the live debrief

---

Good luck.
