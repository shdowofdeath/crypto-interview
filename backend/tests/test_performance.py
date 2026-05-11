"""Performance and correctness tests for the CryptoWatch API.

Run with:
    pytest tests/test_performance.py -v

Run repeatedly to surface flakiness:
    for i in {1..5}; do pytest tests/test_performance.py -v --tb=no -q; done
"""

import asyncio
import time
import pytest
import httpx
from unittest.mock import patch


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


@pytest.mark.asyncio
async def test_prices_endpoint_responds_within_threshold():
    """/api/prices must respond within 2 seconds."""
    from main import app

    def slow_fetch():
        time.sleep(1.8)
        return FAKE_PRICES

    with patch("main.fetch_prices", side_effect=slow_fetch):
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            start = time.monotonic()
            response = await client.get("/api/prices")
            elapsed = time.monotonic() - start

    assert response.status_code == 200
    assert elapsed < 2.0, f"Response took {elapsed:.2f}s — expected < 2.0s"


@pytest.mark.asyncio
async def test_concurrent_requests_complete_faster_than_sequential():
    """Concurrent requests should be much faster than sequential under async I/O."""
    from main import app

    async def mock_fetch():
        await asyncio.sleep(0.3)
        return FAKE_PRICES

    with patch("main.fetch_prices", side_effect=mock_fetch):
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            start_seq = time.monotonic()
            for _ in range(10):
                await client.get("/api/prices")
            sequential_time = time.monotonic() - start_seq

            start_con = time.monotonic()
            await asyncio.gather(*[client.get("/api/prices") for _ in range(10)])
            concurrent_time = time.monotonic() - start_con

    ratio = concurrent_time / sequential_time
    assert ratio < 0.40, (
        f"Concurrent {concurrent_time:.2f}s vs sequential {sequential_time:.2f}s "
        f"(ratio {ratio:.2f})"
    )


@pytest.mark.asyncio
async def test_portfolio_values_consistent_under_concurrent_load():
    """Portfolio calculations must be deterministic under concurrent load."""
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
    assert all(r.status_code == 200 for r in responses)

    first = results[0]
    for i, result in enumerate(results[1:], 1):
        assert result["total_value_usd"] == first["total_value_usd"]
        assert result["total_change_24h_pct"] == first["total_change_24h_pct"]


@pytest.mark.asyncio
async def test_portfolio_weighted_change_matches_value_weighting():
    """A portfolio with one dominant holding should report a 24h change
    close to that holding's change — not the simple mean across holdings."""
    from models.portfolio import compute_portfolio_value

    prices = [
        {"id": "bitcoin",  "symbol": "BTC", "name": "Bitcoin",  "current_price": 60000.0, "market_cap": 0, "price_change_24h": 10.0, "image": "", "last_updated": ""},
        {"id": "ethereum", "symbol": "ETH", "name": "Ethereum", "current_price":  3000.0, "market_cap": 0, "price_change_24h":  0.0, "image": "", "last_updated": ""},
        {"id": "solana",   "symbol": "SOL", "name": "Solana",   "current_price":   100.0, "market_cap": 0, "price_change_24h": -5.0, "image": "", "last_updated": ""},
    ]
    holdings = [
        {"coin_id": "bitcoin",  "quantity": 1.0},
        {"coin_id": "ethereum", "quantity": 0.001},
        {"coin_id": "solana",   "quantity": 0.001},
    ]

    result = compute_portfolio_value(prices, holdings=holdings)
    assert abs(result["total_change_24h_pct"] - 10.0) < 0.01
