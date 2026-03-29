# CryptoWatch — Full-Stack Engineering Challenge

## Overview

CryptoWatch is a live cryptocurrency dashboard with portfolio tracking.

**Stack:**
- Backend: Python + FastAPI, fetches live data from CoinGecko (free, no API key needed)
- Frontend: React + TypeScript + Vite + Tailwind CSS

The app has deliberate bugs and missing features. Your job is to find them, fix them, and extend the app — then open a PR explaining everything you did.

---

## How to Run

### Option A — CodeSandbox (recommended)
Open the repo in CodeSandbox. Two tasks start automatically:
- `Backend (FastAPI :8000)` — installs deps and starts the API server
- `Frontend (Vite :5173)` — installs deps and starts the UI

Preview opens at port `5173`.

### Option B — Local
**Terminal 1 — Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend API + docs: http://localhost:8000/docs

---

## Your Tasks

You have **three categories** of work. Do all three. Each is assessed separately.

---

### Category 1 — Bug Fixes

There are **8 bugs** in the codebase. Find them all, fix them, and explain each one in your PR.

#### Backend Bugs

**B1. Wrong portfolio calculation formula** — `backend/models/portfolio.py`
The 24h percentage change calculation uses an incorrect mathematical formula. The result has wrong magnitude for all inputs and crashes on a specific edge case. Find it, fix it, prove why the current formula is wrong.

**B2. Crash on every real API call** — `backend/services/coingecko.py`
The backend crashes with a `KeyError` every time it tries to call CoinGecko. The wrong field name is being accessed from the API response. Check the actual CoinGecko `/coins/markets` response shape and fix the key. Also add a null guard for a field that can be `None`.

**B3. Blocking I/O in async route** — `backend/services/coingecko.py`
A synchronous HTTP library is used inside an async FastAPI route. This blocks the event loop and serializes all requests under load. Fix it correctly — not just by swapping libraries, but by making the function properly async end-to-end.

**B4. CORS security misconfiguration** — `backend/main.py`
The CORS middleware has a configuration that violates the browser security spec and would expose the API to any origin. Identify exactly why it's wrong, fix it, and explain the security impact.

#### Frontend Bugs

**B5. Prices never load from the backend** — `frontend/src/components/PriceTable.tsx`
The price table always shows hardcoded mock data from January 2024. It never calls the backend API. Replace the mock data with a real fetch to `/api/prices`, with proper loading and error states.

**B6. Refresh interval control doesn't work** — `frontend/src/components/PriceTable.tsx`
The dropdown that controls how often prices refresh has no effect. The interval is always 30 seconds regardless of what the user selects. This is a React hooks bug — find the root cause and fix it.

**B7. Price change colors are inverted** — `frontend/src/components/CryptoCard.tsx`
Coins that went up show in red. Coins that went down show in green. Fix the display so green = positive, red = negative. The bug appears in two places in the component.

**B8. Expanded card details are invisible** — `frontend/src/components/CryptoCard.tsx`
Clicking a coin card should expand it to show market cap and 24h change details. The details render in the DOM but are completely invisible. Find the CSS issue and fix it.

---

### Category 2 — Failing Tests

There is a test suite in `backend/tests/test_performance.py`. Run it:

```bash
cd backend
pytest tests/ -v
```

The tests cover concurrent request performance and portfolio calculation consistency.
**Some tests are flaky** — they fail intermittently even when the code is correct.

Your job:
1. Run the tests multiple times and observe which ones are flaky
2. For each flaky test: identify **why** it's flaky (the root cause in the test itself, not in your code)
3. Fix the flaky tests so they are reliable — without weakening what they assert
4. Make sure all tests pass after your bug fixes are applied

Include a **"Tests" section** in your PR describing what was flaky and how you fixed it.

> Hint: flaky tests are a code smell in themselves. A test that sometimes passes and sometimes fails is worse than no test — it trains engineers to ignore failures.

---

### Category 3 — New Feature

**Add a coin search / filter bar to the price table.**

Requirements:
- Text input above the coin list
- Filters coins in real time as the user types (by name or symbol)
- If no coins match, show a friendly empty state
- Works with both the mock data (before B5 is fixed) and real API data (after)
- Styled consistently with the existing UI

This is intentionally open-ended. Show us how you think about small UI features.

---

### Category 4 — Code Review

Read the entire codebase as if you're reviewing a colleague's PR. In your PR description, include a **"Code Review" section** with:

- At least 3 things you'd flag in a real review (beyond the 8 known bugs)
- At least 1 concern about the backend architecture or reliability
- At least 1 concern about the frontend data fetching approach
- Any security or operational risks you'd raise before this goes to production

There are no wrong answers here — we want to see how you think about production readiness.

---

## Pull Request Requirements

Your PR description must include all of the following sections:

### Bug Fixes
For each bug: file, line number, root cause, fix, and why your fix is correct.

### New Feature
What you built, how it works, any tradeoffs you made.

### Code Review
Your observations from Category 3.

### Test Plan
A checklist of how to verify everything works end-to-end after your fixes.

---

## Evaluation Criteria

| Area | What We Look For |
|---|---|
| Bug identification | Did you find all 8? Do you understand each root cause? |
| Backend depth | Do you understand async Python and the CORS spec? |
| Frontend depth | Do you understand React hooks and closures? |
| Feature quality | Is the search feature clean, correct, and well-integrated? |
| Code review | Do you think beyond the task? What do you catch proactively? |
| Communication | Is your PR description specific, clear, and professional? |

---

## Rules

- Do not add npm/pip packages without justification in the PR
- Do not refactor code unrelated to your fixes or feature
- Do not use explanations you cannot defend — the live debrief will include follow-up questions on every fix

---

## Debugging Tips

```bash
# Test the backend directly
curl http://localhost:8000/health
curl http://localhost:8000/api/prices
curl http://localhost:8000/api/portfolio

# Interactive API docs
open http://localhost:8000/docs
```

The backend error messages are surfaced through the API — if `/api/prices` returns a 502, check the uvicorn terminal for the Python traceback.

---

Good luck.
