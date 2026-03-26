# Answer Key — Interviewer Reference

**DO NOT share this with candidates.**

---

## Bug #1 — Wrong formula for previous price (`backend/models/portfolio.py`)

**Line:** `previous_price = current_price * (1 - pct_change / 100)`

**Root cause:** CoinGecko's `price_change_percentage_24h` represents:
`current = previous * (1 + pct/100)` → so `previous = current / (1 + pct/100)`

The code uses subtraction, producing wrong magnitudes. Edge case: `pct_change = 100`
gives `previous_price = 0` → division-by-zero in the portfolio percentage calc.

**Fix:**
```python
previous_price = current_price / (1 + pct_change / 100)
```

---

## Bug #2 — Wrong CoinGecko response key + no null guard (`backend/services/coingecko.py`)

**Line:** `coin["price_change_percentage_24h_in_currency"]`

**Root cause:** The `/coins/markets` endpoint returns `price_change_percentage_24h`
at the top level. The `_in_currency` suffix only exists in a different response
shape that requires additional query params. This is a `KeyError` on **every** real
API call — the app never loads live data at all.

Secondary: `coin["current_price"]` can be `None` for newly listed coins.

**Fix:**
```python
"price_change_24h": coin.get("price_change_percentage_24h", 0.0),
"current_price": coin.get("current_price") or 0.0,
```

---

## Bug #3 — Blocking sync I/O in async route (`backend/services/coingecko.py`)

**Line:** `import requests` / `response = requests.get(...)`

**Root cause:** `requests.get()` is synchronous. Called from an `async def` FastAPI
route without `run_in_executor`, it blocks the asyncio event loop for the entire
duration of the HTTP call. Under concurrent load, all requests queue serially.

The fix is not just "use httpx" — the function must become `async def` and use
`await` properly. Callers in `main.py` must also `await fetch_prices()`.

**Fix:**
```python
import httpx

async def fetch_prices():
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(...)
        response.raise_for_status()
        return [_parse_coin(coin) for coin in response.json()]
```

---

## Bug #4 — CORS wildcard + credentials (`backend/main.py`)

**Lines:** `allow_origins=["*"], allow_credentials=True`

**Root cause:** The CORS spec forbids `Access-Control-Allow-Origin: *` alongside
`Access-Control-Allow-Credentials: true`. Browsers reject this combination.
Credentialed cross-origin requests from the frontend will silently fail.

Beyond the spec violation: allowing all origins in production means any site can
make requests to this API.

**Fix:**
```python
allow_origins=["http://localhost:5173"],
allow_credentials=True,
allow_methods=["GET", "POST"],
allow_headers=["Content-Type"],
```

---

## Bug #5 — Hardcoded MOCK_DATA, never calls backend (`frontend/src/components/PriceTable.tsx`)

**Lines:** `const MOCK_DATA = [...]` + no-op `fetchData()`

**Root cause:** The component initializes state with hardcoded mock prices and
`fetchData()` never makes an HTTP request. The app always shows January 2024 prices.

**Fix:** Remove MOCK_DATA. Implement real fetch:
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

---

## Bug #6 — Missing useEffect dependency — stale closure (`frontend/src/components/PriceTable.tsx`)

**Line:** `}, []); // missing refreshInterval`

**Root cause:** `setInterval(fetchData, refreshInterval)` captures `refreshInterval`
from the closure at the time the effect runs (initial render = 30000ms). Since
`refreshInterval` is absent from the dependency array, the effect never re-runs when
the user changes the dropdown. The interval control is functionally broken.

**Fix:** `}, [refreshInterval]);`

React will clear the old interval and start a new one with the updated value
whenever `refreshInterval` changes.

---

## Bug #7 — Swapped color classes (`frontend/src/components/CryptoCard.tsx`)

**Lines:** Both `isPositive ? "text-red-400" : "text-green-400"` occurrences

**Root cause:** Conditional is inverted. Positive price change shows red, negative
shows green. Appears in both the row and the expanded detail panel.

**Fix:** `isPositive ? "text-green-400" : "text-red-400"`

---

## Bug #8 — overflow-hidden + h-16 clips expanded card (`frontend/src/components/CryptoCard.tsx`)

**Line:** `className="... overflow-hidden h-16 ..."`

**Root cause:** `h-16` is a fixed 64px height (only enough for the collapsed row).
`overflow-hidden` clips anything extending beyond that. Clicking to expand a card
renders the details panel in the DOM but it's entirely invisible.

**Fix:** Remove both `overflow-hidden` and `h-16`:
```tsx
<div className="bg-gray-800 rounded-xl px-5 py-4 cursor-pointer hover:bg-gray-900 transition-colors">
```

---

## What a Strong PR Description Looks Like

A strong senior candidate will:
- List all 8 bugs with file + line number + root cause (not just symptom)
- Call out Bug #3 as an async/event-loop issue, not just "used wrong library"
- Call out Bug #4 as a CORS spec violation AND a security concern
- Mention that Bug #2 makes the app non-functional with real data
- Add at least 2 proactive concerns (e.g., no rate limiting, no error boundary, requests still in requirements.txt)
- Write a test plan

**Red flags:**
- Misses Bug #3 or describes it only as "use httpx instead"
- Misses Bug #4 entirely or describes it as "just a config preference"
- Doesn't mention the CoinGecko key name mismatch as a crash bug
- PR description lists fixes without root causes
