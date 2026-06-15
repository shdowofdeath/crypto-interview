import time
import httpx
import asyncio
from urllib.parse import urlparse

COINGECKO_URL = "https://api.coingecko.com/api/v3"

COINS = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]

CACHE_TTL_SECONDS = 30.0
REQUEST_TIMEOUT_SECONDS = 10.0

_PRICE_CACHE: dict = {}
_cache_lock = asyncio.Lock()

_client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)


async def fetch_prices():
    """Fetch current prices and 24h change for tracked coins.

    Results are cached at module scope with a 30s TTL. A lock guards the
    fetch-and-populate step so concurrent cold-start requests don't all
    hit the upstream API and race on the cache write.

    Returns:
        list of parsed coin dicts (see `_parse_coin` for the shape).
    """
    now = time.monotonic()
    cached = _PRICE_CACHE.get("prices")
    if cached is not None and cached["expires_at"] > now:
        return cached["data"]

    async with _cache_lock:
        now = time.monotonic()
        cached = _PRICE_CACHE.get("prices")
        if cached is not None and cached["expires_at"] > now:
            return cached["data"]

        response = await _client.get(
            f"{COINGECKO_URL}/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ",".join(COINS),
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h",
            },
        )
        response.raise_for_status()
        raw = response.json()
        parsed = [_parse_coin(coin) for coin in raw]

        _PRICE_CACHE["prices"] = {
            "data": parsed,
            "expires_at": now + CACHE_TTL_SECONDS,
        }
        return parsed


def _parse_coin(coin: dict) -> dict:
    """Parse a single coin entry from CoinGecko response."""
    return {
        "id": coin["id"],
        "symbol": coin["symbol"].upper(),
        "name": coin["name"],
        "current_price": coin["current_price"],
        "market_cap": coin.get("market_cap", 0),
        "price_change_24h": coin["price_change_percentage_24h"],
        "image": coin["image"],
        "last_updated": coin["last_updated"],
    }


async def fetch_image(url: str) -> tuple[bytes, str]:
    """Proxy a coin icon to avoid mixed-content / CORS warnings in the UI."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Unsupported scheme")

    response = await _client.get(url)
    response.raise_for_status()
    return response.content, response.headers.get("content-type", "image/png")


async def aclose_client():
    """Close the shared HTTP client. Call during app shutdown."""
    await _client.aclose()
