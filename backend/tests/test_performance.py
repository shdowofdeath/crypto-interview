"""
Performance tests for the CryptoWatch API.

Run with:
    pytest tests/test_performance.py -v

These tests verify that the API handles concurrent requests efficiently.
If you see intermittent failures, investigate why before assuming the test
is wrong.
"""

import asyncio
import time
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock

# ── Fake price data (avoids hitting real CoinGecko in tests) ──────────────────

FAKE_PRICES = [
    {
        "id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "current_price": 62000.0,
        "market_cap": 1220000000000,
        "price_change_24h": 2.4,
        "image": "https://example.com/btc.png",
        "last_updated": "2024-01-01T00:00:00.000Z",
    },
    {
        "id": "ethereum",
        "symbol": "ETH",
        "name": "Ethereum",
        "current_price": 3100.0,
        "market_cap": 373000000000,
        "price_change_24h": -1.8,
        "image": "https://example.com/eth.png",
        "last_updated": "2024-01-01T00:00:00.000Z",
    },
    {
        "id": "solana",
        "symbol": "SOL",
        "name": "Solana",
        "current_price": 145.0,
        "market_cap": 67000000000,
        "price_change_24h": 5.1,
        "image": "https://example.com/sol.png",
        "last_updated": "2024-01-01T00:00:00.000Z",
    },
]


# ── Test 1: Basic response time ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_prices_endpoint_responds_within_threshold():
    """
    /api/prices must respond within 2 seconds.

    FLAKY: This test uses a real-time sleep inside the mock to simulate
    CoinGecko latency. If the machine is under load, the sleep may take
    longer than expected and push the total time over the threshold —
    causing a spurious failure unrelated to the code being tested.

    A candidate should notice:
    1. The threshold (2.0s) is dangerously close to the simulated latency (1.8s)
    2. time.sleep() inside an async mock is the wrong tool — it blocks the
       event loop and inflates measured time unpredictably
    3. The fix is to use asyncio.sleep() in the mock AND widen the threshold,
       or to decouple latency simulation from wall-clock assertions entirely
    """
    from main import app

    # Simulate CoinGecko taking 1.8 seconds — close to the 2.0s threshold
    def slow_fetch():
        time.sleep(1.8)  # BUG: blocks event loop in async context
        return FAKE_PRICES

    with patch("main.fetch_prices", side_effect=slow_fetch):
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            start = time.monotonic()
            response = await client.get("/api/prices")
            elapsed = time.monotonic() - start

    assert response.status_code == 200
    # FLAKY: threshold is too tight — any OS scheduling jitter causes failure
    assert elapsed < 2.0, f"Response took {elapsed:.2f}s — expected < 2.0s"


# ── Test 2: Concurrent request throughput ────────────────────────────────────

@pytest.mark.asyncio
async def test_concurrent_requests_complete_faster_than_sequential():
    """
    10 concurrent requests to /api/prices should complete significantly
    faster than 10 sequential requests — proving the endpoint handles
    concurrency correctly (i.e. fetch_prices is truly async).

    FLAKY: The ratio check (concurrent must be < 40% of sequential time)
    is environment-dependent. On a slow CI machine or CodeSandbox, both
    sequential and concurrent may run slowly, and the ratio may not hold.

    A candidate should notice:
    1. The mock uses asyncio.sleep correctly — but the RATIO assertion is
       the flaky part, not the sleep
    2. This test proves nothing if fetch_prices() is still synchronous
       (Bug #3 unfixed) — both times will be similar and the test may pass
       by accident depending on sleep precision
    3. The fix: assert on absolute time bounds per request, not ratios.
       Or: explicitly assert that concurrent time < (N * per_request_latency),
       which is the actual invariant being tested.
    """
    from main import app

    call_count = 0

    async def mock_fetch():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.3)  # simulate 300ms CoinGecko latency
        return FAKE_PRICES

    with patch("main.fetch_prices", side_effect=mock_fetch):
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:

            # Sequential: 10 requests one after another
            start_seq = time.monotonic()
            for _ in range(10):
                await client.get("/api/prices")
            sequential_time = time.monotonic() - start_seq

            call_count = 0

            # Concurrent: 10 requests fired at the same time
            start_con = time.monotonic()
            await asyncio.gather(*[client.get("/api/prices") for _ in range(10)])
            concurrent_time = time.monotonic() - start_con

    # FLAKY: ratio is environment-sensitive — may fail on slow machines
    ratio = concurrent_time / sequential_time
    assert ratio < 0.40, (
        f"Concurrent requests ({concurrent_time:.2f}s) should be much faster "
        f"than sequential ({sequential_time:.2f}s), but ratio was {ratio:.2f}. "
        f"Is fetch_prices() truly async? (Bug #3)"
    )


# ── Test 3: Portfolio calculation correctness under load ──────────────────────

@pytest.mark.asyncio
async def test_portfolio_values_consistent_under_concurrent_load():
    """
    Portfolio calculations must be deterministic — the same input prices
    must always produce the same output, even under concurrent load.

    FLAKY: This test fires 20 concurrent portfolio requests and checks that
    all results are identical. In a correct implementation this always passes.
    But if there is any shared mutable state in compute_portfolio_value()
    (e.g. a module-level cache that gets partially updated), concurrent access
    can produce different results on different runs.

    A candidate should notice:
    1. The test itself is correct — but it surfaces a latent bug IF the
       candidate introduces a naive caching layer to fix the rate limiting
       concern from the code review section
    2. The flakiness only manifests when a cache is added without a lock
    3. This is the test that catches "works on my machine" threading bugs
    """
    from main import app

    async def mock_fetch():
        await asyncio.sleep(0.05)
        return FAKE_PRICES

    with patch("main.fetch_prices", side_effect=mock_fetch):
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            responses = await asyncio.gather(
                *[client.get("/api/portfolio") for _ in range(20)]
            )

    results = [r.json() for r in responses]

    assert all(r.status_code == 200 for r in responses), (
        "Some portfolio requests failed under concurrent load"
    )

    # All 20 results must be identical
    first = results[0]
    for i, result in enumerate(results[1:], 1):
        assert result["total_value_usd"] == first["total_value_usd"], (
            f"Request {i} returned different total_value_usd: "
            f"{result['total_value_usd']} vs {first['total_value_usd']}. "
            f"Possible shared mutable state in compute_portfolio_value()."
        )
        assert result["total_change_24h_pct"] == first["total_change_24h_pct"], (
            f"Request {i} returned different total_change_24h_pct — "
            f"possible race condition in portfolio calculation."
        )
