# CryptoWatch — Staff Engineering Challenge

## Overview

CryptoWatch is a live cryptocurrency dashboard with portfolio tracking.

**Stack**
- Backend: Python 3.11 + FastAPI, fetches live data from CoinGecko (free, no API key required)
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS

This codebase was inherited from a previous engineer. It has correctness bugs, performance bugs, security bugs, and reliability bugs. None of them are commented. Your job is to find them, explain them, fix them — and ship a feature on top.

You should treat this the way you'd treat any production system you're newly on call for: read first, ask questions of the code, run things, look at logs.

---

## How to Run

Both servers run with **hot reload** out of the box. Save a file and the change is live.

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

The backend logger prints every request, every upstream call, and every exception to stdout. Keep that terminal visible — it is your debugger.

---

## What We Want From You

Four categories of work. All four are evaluated.

### 1. Bug Hunt

There are **10–15 bugs** spread across backend, frontend, and tests. They span:

- Correctness — wrong math, wrong aggregation, edge-case crashes
- Concurrency — races, stale state, blocking I/O in async paths
- Security — input validation, output handling, secrets, request forgery
- Reliability — error handling, timeouts, swallowed failures
- UI — colour semantics, layout, state propagation

We are **not** going to tell you which file each bug is in. We are not going to confirm a number. You should expect to find more than you think on the first pass.

For each bug, in your PR description write:
1. File + line
2. Symptom (how would a user notice it?)
3. Root cause (one or two sentences)
4. Fix (what you changed, and why your fix is correct rather than a workaround)

### 2. Flaky Tests

`backend/tests/test_performance.py` contains tests that fail intermittently. Run them many times:

```bash
cd backend
for i in {1..10}; do pytest tests/ --tb=no -q; done
```

For each flaky test: identify why it's flaky, fix it without weakening what it asserts, and write a short note about it in your PR.

One of the tests fails **deterministically** after a bug fix you ship. That's intended — the test is correct, and the existing code is wrong.

### 3. Feature — Price Alerts (build it)

Users want to be notified when a coin crosses a price threshold. Build it.

**Must-haves**
- A user can create an alert: pick a coin, pick a direction (`above` / `below`), pick a price
- A user can see their list of active alerts and delete them
- When the current price crosses an active alert's threshold, the alert fires exactly once and is marked as triggered

**Out of scope (don't build, but mention in your PR if relevant)**
- Real authentication — assume a single user for now
- Push notifications, email, SMS — surfacing the fire in the UI is enough

The backend has stub endpoints at `/api/alerts` (see `backend/main.py`) — finish them. Persistence layer is your call.

**This task is intentionally underspecified.** You decide the data shape, the storage, the polling strategy, the UI. Defend your choices in the PR. We care more about how you reason than which library you picked.

### 4. Code Review — Colleague's PR

Read `REVIEW_PR/PR_DESCRIPTION.md` and `REVIEW_PR/REVIEW_PR.diff`.

A teammate has opened a PR to add rate limiting and response caching. They've asked you for a review before they merge. Write your review as if you're posting it on GitHub — inline-style comments are fine.

We're looking for:
- Concrete issues you'd block on, with line refs
- Design feedback (would you take a different approach? why?)
- Anything that would surprise you in production
- What you would *not* flag, and why (taste matters)

There is no minimum number of comments. A short, sharp review beats a long noisy one.

---

## PR Requirements

Open one PR with all your work. Title it `CryptoWatch take-home — <your name>`.

Your PR description must contain four sections, in this order:

1. **Bug Fixes** — table or list, one row per bug, with the four fields above
2. **Tests** — what was flaky, what you changed, what still needs human attention
3. **Feature** — what you built, what tradeoffs you made, what you'd do next with another day
4. **Review of REVIEW_PR** — your review comments

---

## Live Debrief

After we read your PR, we'll schedule a 60-minute debrief. We will pick three of your bug-fix entries at random and ask you to defend them — including the math, the threat model, or the React semantics. We will also walk through your feature with the lens "what breaks first at 10k users."

If you used an LLM, that's fine. If you can't defend an explanation it wrote, that's not.

---

## Rules

- Don't add npm/pip packages without a one-line justification in the PR
- Don't refactor unrelated code
- Don't suppress lint warnings without a reason
- Don't `// @ts-expect-error` or `# type: ignore` without a comment explaining why
- If you find a bug we didn't list, surface it. Bugs we didn't plan count for full credit.

---

## Pointers

- `backend/services/coingecko.py` is where upstream calls live
- `backend/models/portfolio.py` is where the math lives
- `frontend/src/components/PortfolioSummary.tsx` is clean — use it as the reference for how a React component in this codebase *should* look
- `DEBUGGING_GUIDE.md` has commands and symptom-to-tool hints. It deliberately does **not** name any bug.

Good luck.
