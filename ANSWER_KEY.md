# Answer Key — Interviewer Reference

**DO NOT share this with candidates.**

---

## Running the App (Verified Commands)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Quick health check
```bash
curl http://localhost:8000/health          # → {"status":"ok"}
curl http://localhost:8000/api/prices      # crashes with KeyError until Bug #2 fixed
curl http://localhost:8000/api/portfolio   # crashes with KeyError until Bug #2 fixed
```

---

## Bug #1 — Wrong portfolio formula (`backend/models/portfolio.py`)

**Line:** `previous_price = current_price * (1 - pct_change / 100)`

**Root cause:** CoinGecko's `price_change_percentage_24h` means:
`current = previous * (1 + pct/100)` → so `previous = current / (1 + pct/100)`

The code uses subtraction, producing wrong magnitudes. Edge case: `pct_change = 100`
gives `previous_price = 0` → division-by-zero in the percentage calc.

**Fix:**
```python
previous_price = current_price / (1 + pct_change / 100)
```

**Strong answer:** candidate derives the math from first principles, identifies the division-by-zero edge case, and verifies with a concrete example (e.g. price = $100, pct = 10%).

---

## Bug #2 — Wrong CoinGecko key + no null guard (`backend/services/coingecko.py`)

**Line:** `coin["price_change_percentage_24h_in_currency"]`

**Root cause:** The `/coins/markets` endpoint returns `price_change_percentage_24h`
at the top level. The `_in_currency` suffix only exists in a different response shape.
This is a `KeyError` on **every** real API call — the app never loads live data.

Secondary: `coin["current_price"]` can be `None` for newly listed coins.

**Fix:**
```python
"price_change_24h": coin.get("price_change_percentage_24h", 0.0),
"current_price": coin.get("current_price") or 0.0,
```

**Strong answer:** candidate checked the actual CoinGecko API docs or tested the raw response to confirm the correct key name.

---

## Bug #3 — Blocking sync I/O in async route (`backend/services/coingecko.py`)

**Line:** `import requests` / `response = requests.get(...)`

**Root cause:** `requests.get()` is synchronous. Called from an `async def` FastAPI
route without `run_in_executor`, it blocks the asyncio event loop for the duration
of the HTTP call. Under concurrent load, all requests queue serially.

The fix is not just "use httpx" — the function must become `async def` and use `await`.
Callers in `main.py` must also `await fetch_prices()`.

**Fix:**
```python
import httpx

async def fetch_prices():
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{COINGECKO_URL}/coins/markets",
            params={...},
        )
        response.raise_for_status()
        return [_parse_coin(coin) for coin in response.json()]
```

And in `main.py`:
```python
prices = await fetch_prices()
```

**Strong answer:** candidate explains the event loop, mentions `run_in_executor` as an alternative, and knows to remove `requests` from requirements.txt.

---

## Bug #4 — CORS wildcard + credentials (`backend/main.py`)

**Lines:** `allow_origins=["*"], allow_credentials=True`

**Root cause:** The CORS spec forbids `Access-Control-Allow-Origin: *` with
`Access-Control-Allow-Credentials: true` simultaneously. Browsers reject this.
Beyond the spec: wildcard origin means any website can make cross-origin requests.

**Fix:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

**Strong answer:** candidate cites the spec, explains why browsers reject the combo, and suggests reading the allowed origin from an env var for production.

---

## Bug #5 — Hardcoded MOCK_DATA (`frontend/src/components/PriceTable.tsx`)

**Root cause:** `coins` is initialized with `MOCK_DATA` and `fetchData()` is a no-op.

**Fix:**
```tsx
const [coins, setCoins] = useState<Coin[]>([]);
const [loading, setLoading] = useState(true);

const fetchData = async () => {
  try {
    setLoading(true);
    const res = await fetch("/api/prices");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    setCoins(json.data);
  } catch (err) {
    setError(err instanceof Error ? err.message : "Unknown error");
  } finally {
    setLoading(false);
  }
};
```

**Strong answer:** candidate points to `PortfolioSummary.tsx` as the existing correct pattern and follows it consistently.

---

## Bug #6 — Missing useEffect dependency (`frontend/src/components/PriceTable.tsx`)

**Line:** `}, []); // missing refreshInterval`

**Root cause:** `setInterval(fetchData, refreshInterval)` captures `refreshInterval`
from the closure at first render (30000ms). The effect never re-runs, so changing
the dropdown has no effect on actual polling frequency.

**Fix:** `}, [refreshInterval]);`

**Strong answer:** candidate explains JS closure semantics, why React's dependency array exists, and what re-running the effect does (clears old interval, starts new one).

---

## Bug #7 — Swapped colors (`frontend/src/components/CryptoCard.tsx`)

**Lines:** Both `isPositive ? "text-red-400" : "text-green-400"` occurrences

**Fix:** `isPositive ? "text-green-400" : "text-red-400"` (both places)

---

## Bug #8 — overflow-hidden + h-16 clips expanded card (`frontend/src/components/CryptoCard.tsx`)

**Line:** `className="... overflow-hidden h-16 ..."`

**Root cause:** Fixed 64px height + overflow:hidden clips the details panel entirely.

**Fix:** Remove both `overflow-hidden` and `h-16` from the container div.

---

## Feature — Search / Filter Bar

A correct implementation:

```tsx
// In PriceTable.tsx — add state
const [search, setSearch] = useState("");

// Filter coins
const filtered = coins.filter(
  (c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.symbol.toLowerCase().includes(search.toLowerCase())
);

// Render input above the list
<input
  type="text"
  placeholder="Search coins..."
  value={search}
  onChange={(e) => setSearch(e.target.value)}
  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 mb-4"
/>

// Use `filtered` instead of `coins` in the map
{filtered.length === 0 ? (
  <p className="text-center text-gray-500 py-8 text-sm">No coins match "{search}"</p>
) : (
  filtered.map((coin) => <CryptoCard key={coin.id} coin={coin} />)
)}
```

**Strong answer:** case-insensitive search, empty state, no unnecessary state (filter is derived), styled consistently.

---

## Code Review — What Strong Candidates Flag

Beyond the 8 bugs, strong candidates raise:

1. **No rate limiting** — CoinGecko free tier ~30 req/min. With multiple users/tabs polling every 5s this hits limits fast. Needs a server-side cache (e.g. TTL cache on the prices response).
2. **`requests` still in requirements.txt** — dead dependency after Bug #3 fix, misleading and could cause future regressions.
3. **No error boundary in React** — a JS error in one component crashes the entire app.
4. **Portfolio holdings are hardcoded** — no persistence, no user input. Fine for demo but should be documented.
5. **No input validation on API endpoints** — `/api/portfolio` accepts arbitrary query params with no validation.
6. **Uvicorn `--reload` in production** — the Dockerfile uses `--reload` which is for development only.
7. **No retry logic** — if CoinGecko is briefly unavailable, the entire app shows an error with no retry.

---

## Scoring Guide

| Score | What it means |
|---|---|
| Found all 8 bugs with correct root causes | Strong pass |
| Found 6-7 bugs, missed 1-2 subtle ones | Pass |
| Found < 6 bugs or described symptoms not causes | Discuss in debrief |
| Feature works correctly and is well-integrated | Strong pass |
| Feature works but has edge cases or style issues | Pass |
| Code review surfaces real production concerns | Senior signal |
| Code review only restates the 8 bugs | Junior signal |
