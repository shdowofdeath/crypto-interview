# [PERF-142] Add response cache + per-IP rate limiting to /api/prices

## Context

CoinGecko's free tier rate-limits us at ~30 req/min. We've been getting 429s during traffic spikes, which cascade into 502s for our users. This PR adds:

1. An in-memory response cache for `/api/prices` (60s TTL)
2. Per-IP rate limiting on all `/api/*` endpoints (60 req/min)

This unblocks the marketing campaign launch on Monday.

## Changes

- New `backend/middleware/rate_limit.py` — sliding-window rate limiter
- New `backend/cache.py` — module-level dict cache with TTL
- Wired both into `main.py`
- Added `X-RateLimit-Remaining` header so the frontend can show a warning when users get close to the limit

## Testing

- Manually verified with `ab -n 200 -c 10 http://localhost:8000/api/prices`
- Cache hit rate looked good in local testing (~95%)
- 60 req/min limit confirmed by hitting the endpoint 61 times in a row — the 61st returned 429

## Deployment

- Deploy to staging, soak for an hour, deploy to prod
- No DB migrations
- Should be safe to roll back if we see issues

## Open Questions

- Should the cache key include the user? Right now it's a single global key — that's fine because `/api/prices` returns the same data for everyone, but worth flagging.
- Memory growth — the rate limiter dict grows unbounded. I added a TODO. Worth doing in a follow-up?

Requesting review from: @candidate
