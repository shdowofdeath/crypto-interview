# Debugging Guide

Stuck? Use this guide. It tells you *where* to look and *what to think about* — not what to fix.

---

## How to Debug This App

### Check if the backend is alive
```bash
curl http://localhost:8000/health
```
If this fails → uvicorn isn't running. Check the backend terminal for errors.

### Check what the backend actually returns
```bash
curl http://localhost:8000/api/prices
curl http://localhost:8000/api/portfolio
```
Error responses include a `detail` field with the Python exception. Read it carefully.

### Interactive API docs
```
http://localhost:8000/docs
```
Try each endpoint directly from the browser. The response body will show you exactly what's failing.

### Watch backend logs
The uvicorn terminal prints every request and every Python traceback in real time. If the UI shows an error, check the backend terminal first.

---

## Hints by Symptom

### "Portfolio unavailable: HTTP 500"
The backend is crashing before it can return data. Check:
- What does `curl http://localhost:8000/api/portfolio` return?
- What does the uvicorn terminal say when that request comes in?
- Look at how the backend parses the external API response — is it accessing the right fields?

### "Prices show January 2024 data / never update"
The frontend may not be calling the backend at all. Check:
- Open browser DevTools → Network tab → do you see any requests to `/api/prices`?
- Look at how `PriceTable.tsx` initializes its state and what `fetchData()` actually does

### "Changing the refresh interval does nothing"
The interval control renders correctly but has no effect. Check:
- How does React's `useEffect` work with values from the component's scope?
- What happens to a `setInterval` that was created with a captured value when that value changes?
- Read the React docs on [useEffect dependencies](https://react.dev/reference/react/useEffect#specifying-reactive-dependencies)

### "Price change % is the wrong color"
A visual bug — no network calls needed to reproduce. Check:
- What does `isPositive` evaluate to for a coin that went up vs down?
- Trace the `className` conditional in `CryptoCard.tsx`

### "Clicking a card doesn't expand it"
The state toggles (add a `console.log` to verify), but nothing appears. Check:
- Open DevTools → Elements tab → click a card → does the detail panel appear in the DOM?
- If yes: why is it not visible? Inspect the computed CSS on the card container

### "Tests fail intermittently"
Run `pytest tests/ -v` multiple times. If the same test sometimes passes and sometimes fails:
- Is the failure deterministic or timing-dependent?
- Does the test assertion depend on wall-clock time? On ratios? On ordering?
- A reliable test must produce the same result on any machine at any load

### Backend works but frontend shows error
- Check the browser Console tab for JS errors
- Check the Network tab — is the request reaching the backend? What status code comes back?
- The Vite proxy forwards `/api/*` to `localhost:8000` — is the backend running on port 8000?

---

## Useful Commands

```bash
# Run backend tests
cd backend && pytest tests/ -v

# Run tests multiple times to surface flakiness
cd backend && for i in {1..5}; do pytest tests/test_performance.py -v --tb=no -q; done

# Check what Python packages are installed
pip list | grep -E "fastapi|httpx|requests|pytest"

# Check what a real CoinGecko response looks like
curl "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&order=market_cap_desc&per_page=1&page=1&price_change_percentage=24h" | python3 -m json.tool
```

The last command shows you the exact shape of the CoinGecko API response — useful for verifying field names.

---

## General Advice

- **Read error messages fully.** Python tracebacks tell you the exact file, line, and exception. Don't skim them.
- **Test one layer at a time.** Confirm the backend works with `curl` before debugging the frontend.
- **Use the browser DevTools.** Network tab, Console tab, and Elements tab will solve most frontend issues.
- **The comments in the code are honest.** If a comment says something looks off, it probably is.
- **`PortfolioSummary.tsx` is clean.** If you're not sure how something should be done in React, look at how that component does it.
