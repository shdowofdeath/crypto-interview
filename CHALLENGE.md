# CryptoWatch — Engineering Challenge

## Overview

CryptoWatch is a live cryptocurrency dashboard with portfolio tracking.

**Stack**
- Backend: Python 3.11 + FastAPI, fetches live data from CoinGecko (free, no API key required)
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS

This codebase was inherited from a previous engineer. It has bugs spanning correctness, concurrency, security, and reliability. Your job is to find some of them, explain them, and review your teammate's PR.

Treat this the way you'd treat a production system you just got paged on: read first, run it, look at logs, then act.

---

## How to Run

Both servers run with **hot reload**. Save a file and the change is live.

### Option A — CodeSandbox
Open the repo in CodeSandbox. Two tasks start automatically:
- `Backend (FastAPI :8000)` — installs deps, runs `uvicorn --reload`
- `Frontend (Vite :5173)` — installs deps, runs `vite` with HMR

Preview opens at port `5173`. Backend OpenAPI at `:8000/docs`.

### Option B — Local

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

- Frontend: <http://localhost:5173>
- Backend: <http://localhost:8000/docs>

The backend logs every request, every upstream call, and every exception. Keep that terminal visible — it is your debugger.

---

## What We Want From You

Four short tasks. Do what you can in the time available. Quality beats quantity on every one of them.

### 1. Find any 3 bugs

There are bugs across the codebase — correctness, concurrency, security, reliability, UI. We are not telling you where they are or how many there are.

**Find any 3 and write them up.** For each:
- File + line
- One sentence on the symptom
- One sentence on the root cause
- The fix (committed to your branch, or pasted as a diff in the PR if quicker)

We care more about *which* 3 you pick and how well you explain them than how many you found. A sharp write-up of one nasty bug beats a list of five obvious ones.

If you spot more than 3 while reading, mention them by name in your PR — no need to fully write them up.

### 2. The Tests

```bash
cd backend
pytest tests/ -v
```

One test fails deterministically. The test is correct — the code is wrong. Identify which test, explain why it's failing, and (if you've already fixed the underlying bug as part of task 1) confirm the test passes.

Other tests in this file are flaky. You don't need to fix them — just note in your PR that they exist and one sentence on what makes them flaky.

### 3. Code Review

Open `REVIEW_PR/PR_DESCRIPTION.md` and `REVIEW_PR/REVIEW_PR.diff`.

A teammate is asking for review before merging a rate-limiting + caching PR. Write the review as if you were posting it on GitHub: inline-style comments with line refs are fine.

We are looking for:
- Concrete issues you'd block on
- One design-level concern (would you take a different approach? why?)
- One thing you'd *not* flag, with a one-line reason (taste matters)

A short, sharp review beats a long noisy one. 3–5 substantive comments is plenty.

### 4. Small Feature

The backend has a stub `GET /api/alerts` endpoint in `backend/main.py` that returns 501. Implement it — return a hardcoded list of 1–2 sample price alerts in whatever response shape you think is right.

We're looking at: your Pydantic model design, the response shape (would you put it in an envelope? flat list? include pagination metadata?), and the one-line defence of your choice in the PR.

Don't wire it to the frontend. Don't add persistence. Don't build the create/delete endpoints.

---

## PR Description

Open one PR. Keep the description short. We suggest these sections:

- **Bugs** — your 3 (+ any extras flagged by name)
- **Test** — which test fails and why
- **Code Review** — your review of `REVIEW_PR/`
- **Alerts endpoint** — what shape you returned and why

A bulleted list is fine. We don't need formal headings or markdown gymnastics.

---

## Live Debrief

After we read your PR, we'll have a short call. We will pick one of your bug write-ups and one of your code-review comments and ask you to defend them — including the math, the threat model, or the React semantics.

If you used an LLM, that's fine. If you can't defend an explanation it wrote, that's not.

---

## Rules

- Don't add npm/pip packages without a one-line justification
- Don't refactor unrelated code
- If you find a bug we didn't list, surface it — bugs we didn't plan count for full credit

---

## Pointers

- `backend/services/coingecko.py` — upstream HTTP calls
- `backend/models/portfolio.py` — the math
- `backend/main.py` — routes, including the alerts stub
- `frontend/src/components/PortfolioSummary.tsx` — the clean reference component
- `DEBUGGING_GUIDE.md` — commands and symptom-to-tool hints (does not name any bug)

Good luck.
