import requests  # BUG #3: should be httpx with async

COINGECKO_URL = "https://api.coingecko.com/api/v3"

COINS = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]


def fetch_prices():
    """Fetch current prices and 24h change for tracked coins.

    BUG #3: This function uses requests.get() — a synchronous blocking call.
    When called from an async FastAPI route, it blocks the entire asyncio
    event loop until the HTTP request completes. Under concurrent load, all
    requests queue behind each other instead of being handled concurrently.

    Fix: convert to `async def fetch_prices()` using httpx.AsyncClient,
    then await the response. Update callers in main.py to `await fetch_prices()`.
    """
    response = requests.get(
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
        timeout=10,
    )
    response.raise_for_status()
    raw = response.json()
    return [_parse_coin(coin) for coin in raw]


def _parse_coin(coin: dict) -> dict:
    """Parse a single coin entry from CoinGecko response."""
    return {
        "id": coin["id"],
        "symbol": coin["symbol"].upper(),
        "name": coin["name"],
        # BUG #2a: current_price can be None for newly listed coins — no guard
        "current_price": coin["current_price"],
        "market_cap": coin.get("market_cap", 0),
        # BUG #2b: wrong key — CoinGecko returns `price_change_percentage_24h`,
        # not `price_change_percentage_24h_in_currency`. The _in_currency suffix
        # only exists in a different endpoint variant. This causes a KeyError
        # on every real API response.
        "price_change_24h": coin["price_change_percentage_24h_in_currency"],
        "image": coin["image"],
        "last_updated": coin["last_updated"],
    }
