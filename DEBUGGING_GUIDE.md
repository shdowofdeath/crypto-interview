# Debugging Guide

This is a generic toolbox. It does **not** tell you where any bug is.

---

## Hot Reload

Both servers reload on save:
- Backend — `uvicorn --reload` watches every `.py` file under `backend/`. Save a file → uvicorn restarts → next request hits new code.
- Frontend — Vite HMR. Save a `.tsx` / `.ts` / `.css` file → the browser updates without losing component state.

If a save doesn't reflect, check the relevant terminal — there's almost certainly a syntax error printed there.

---

## Backend Logs

The backend prints a structured access log for every request:

```
14:22:17 INFO    cryptowatch :: GET /api/portfolio -> 200  (12.4 ms)
```

`logging_config.py` configures the root logger. `cryptowatch` is the main module logger; service-layer loggers can be added with `logging.getLogger(__name__)`.

Watch this terminal while you work. Most backend bugs surface there before they surface in the UI.

## Frontend Logs

Browser DevTools:
- **Network** — every `/api/*` call. Status, payload, timing.
- **Console** — React warnings, your `console.log`s, runtime exceptions.
- **Elements** — DOM + computed CSS. Useful when something "should" render but doesn't.

---

## Probing the API

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/prices
curl http://localhost:8000/api/portfolio

# OpenAPI playground
open http://localhost:8000/docs

# What does CoinGecko actually return?
curl "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&price_change_percentage=24h" | python3 -m json.tool
```

---

## Tests

```bash
cd backend
pytest tests/ -v

# Surface flakiness
for i in {1..10}; do pytest tests/ --tb=no -q; done
```

A test that sometimes passes and sometimes fails is a bug in the test, in the code, or both. Don't `pytest.mark.flaky` it away.

---

## General Advice

- Read tracebacks fully. Python tells you the exact file, line, and exception.
- Test one layer at a time. Confirm the backend works with `curl` before debugging the frontend.
- Trust the rendered output more than the source. UIs lie when the source looks right.
- The comments in the code (where they exist) document intent, not problems. They are not pointing at bugs.
- `PortfolioSummary.tsx` is the reference component. If you're not sure how React should look here, copy its shape.
