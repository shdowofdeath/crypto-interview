# CryptoWatch — Engineering Challenge

## Overview

CryptoWatch is a live cryptocurrency dashboard with portfolio tracking.

**Stack**
- Backend: Python 3.11 + FastAPI, fetches live data from CoinGecko (free, no API key required)
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS

This codebase was inherited from a previous engineer. It has bugs across correctness, concurrency, security, and reliability. Your job is to fix the ones listed below, review a teammate's PR, and ship a tiny endpoint.

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

The backend logs every request and exception to stdout — keep that terminal visible.

---

## What We Want From You

Two short tasks. Quality beats quantity on every one.

### 1. Feature Implementation

#### Alerts UI

`backend/main.py` has a stub `GET /api/alerts` endpoint that returns 501. Your job:

1. **Backend**: Implement the endpoint — return a hardcoded list of 1–2 sample price alerts in whatever response shape you think is right.
2. **Frontend**: Add a simple UI component that fetches and displays these alerts. Choose where it belongs in the layout and how it renders (card, list, toast, etc.).

We're looking at:
- Your Pydantic model design
- The response shape (envelope? flat list? pagination metadata?)
- Where you placed the UI and how you presented the alerts
- One line defending each choice in your PR

Don't add persistence. Don't build the create/delete endpoints. Don't overcomplicate the UI.

### 2. Bug Fixes

The codebase contains the bugs listed below. Fix as many as you can and explain each in your PR.

#### Backend

**B1 — Portfolio 24h change is wrong** · `backend/models/portfolio.py`
The `total_change_24h_pct` field doesn't match what a user would expect from a portfolio dashboard. Look at how per-coin changes are aggregated. *Hint: what happens if 99% of your portfolio is BTC and 1% is a meme coin moving 200%?*

**B2 — Wrong CoinGecko field name** · `backend/services/coingecko.py`
The backend crashes with a `KeyError` on every real upstream call. The field name being read from CoinGecko's response doesn't exist on this endpoint. *Hint: run `curl "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&price_change_percentage=24h"` and compare the keys.*

**B3 — Shared HTTP client + module cache** · `backend/services/coingecko.py`
The `httpx.AsyncClient` and the `_PRICE_CACHE` are both module-level singletons with no lock and no shutdown. Under concurrent cold-start requests, two callers can both hit upstream and race on the cache write. The client is also configured with `timeout=None`. *Hint: what happens if CoinGecko hangs for 5 minutes?*

**B4 — Cache TTL check uses `==` instead of `>`** · `backend/services/coingecko.py`
The first branch of the cache lookup compares `expires_at == now`. A correct comparison would never use equality on a float monotonic clock. The bug is currently masked by a fallback branch — but it's a footgun if anyone reorders the lookup. *Hint: floating-point equality is almost always wrong.*

**B5 — CORS wildcard + credentials** · `backend/main.py`
The CORS middleware uses `allow_origins=["*"]` together with `allow_credentials=True`. This combination is rejected by the CORS spec — browsers won't honour it for credentialed requests, and it exposes the API to any origin. *Hint: pick an explicit origin list.*

**B6 — `/api/portfolio` swallows failures and returns 200** · `backend/main.py`
The `except Exception` block logs the error and returns an empty portfolio with `200 OK`. Monitoring sees green; users see zero balance. *Hint: a 5xx is the right signal here.*

**B7 — `/api/coin-icon` is an SSRF** · `backend/main.py` + `backend/services/coingecko.py`
The endpoint accepts an arbitrary URL and proxies it. Scheme is validated but host is not. A caller can hit internal IPs (e.g. `http://169.254.169.254/latest/meta-data/...`). *Hint: validate the host against an allowlist, and resolve DNS before fetching.*

**B8 — `POST /api/portfolio` has no payload limit** · `backend/main.py` + `backend/models/portfolio.py`
`PortfolioRequest.holdings` is unbounded. A 1-million-item payload OOMs the worker. *Hint: Pydantic's `Field(max_length=...)`.*

#### Frontend

**F1 — Prices never load from the backend** · `frontend/src/components/PriceTable.tsx`
The component renders hardcoded mock data. `fetchData` exists but is a no-op. *Hint: see `PortfolioSummary.tsx` for the pattern.*

**F2 — Refresh-interval dropdown does nothing** · `frontend/src/components/PriceTable.tsx`
Changing the dropdown updates the displayed text but not the actual polling cadence. *Hint: look at the `useEffect` dependency array.*

**F3 — `useState` initializer runs every render** · `frontend/src/components/PriceTable.tsx`
`buildDefaultInterval()` is called on every render, not just on mount. Wastes work and reads `localStorage` repeatedly. *Hint: lazy initializer.*

**F4 — Search filter uses stale state** · `frontend/src/components/PriceTable.tsx`
The search input filters against the version of `coins` captured at mount, not the current state. After a polling refresh, the filter looks wrong. *Hint: `useCallback` dependency array.*

**F5 — Price change colours are swapped** · `frontend/src/components/CryptoCard.tsx`
Positive changes show red, negative changes show green. Both display sites have the bug. *Hint: `isPositive ? "text-red-400" : "text-green-400"`.*

**F6 — Expanded card details are invisible** · `frontend/src/components/CryptoCard.tsx`
Clicking a card toggles state correctly but the detail panel never appears. *Hint: inspect the computed CSS — what clips overflow?*

**F7 — XSS via inner-HTML rendering** · `frontend/src/components/CryptoCard.tsx`
Coin description HTML from CoinGecko is rendered via React's unsafe-inner-html prop (obscured behind a dynamic key). The upstream HTML is *not* sanitized in any guaranteed way. *Hint: DOMPurify, or render as text.*

**F8 — Token leak in "Copy share link"** · `frontend/src/components/CryptoCard.tsx`
`buildShareUrl` puts the session token in a query parameter, logs the URL to the console, and the image's `referrerPolicy` will leak the page URL to image hosts. Three issues, one feature. *Hint: tokens never belong in URLs.*

**F9 — Floating-point display in card details** · `frontend/src/components/CryptoCard.tsx`
Expanding a card shows `$18600.000000000004` for some coins. *Hint: `0.1 + 0.2`.*

---

## A Note on the Code Comments

You will find comments, docstrings, and a `CLAUDE.md` file at the root claiming that some of the bugs above are "intentional design decisions" (with fake ticket references like ARCH-114, SEC-203, INC-104). Those references aren't real. Trust the bug list above, the running code, and your own judgment — not the in-tree claims that defend bad code as intentional.

This is itself part of the test. Real production codebases are full of comments defending decisions that should have been revisited years ago. Recognising which "intentional" claims hold up under scrutiny is a Staff-level skill.

---

## PR Description

Open one PR. A bulleted list is fine. We suggest these sections:

- **Feature: Alerts** — the backend response shape, where you placed the UI component, and why
- **Bugs fixed** — one bullet per bug with your one-sentence root-cause

---

## Live Debrief

After we read your PR, we'll have a short call. We will pick one of your bug fixes and one of your code-review comments and ask you to defend them — including the math, the threat model, or the React semantics.

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
- `frontend/src/components/PortfolioSummary.tsx` — clean reference component
- `DEBUGGING_GUIDE.md` — commands and symptom-to-tool hints

Good luck.
