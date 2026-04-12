from pydantic import BaseModel
from typing import List


class Holding(BaseModel):
    coin_id: str
    quantity: float


class PortfolioRequest(BaseModel):
    holdings: List[Holding] = []


def compute_portfolio_value(prices: list, holdings: list = None) -> dict:
    """
    Compute total portfolio value and 24h percentage change.

    Uses a default demo portfolio if no holdings are provided.
    """
    if holdings is None:
        # Demo portfolio: 0.5 BTC, 2 ETH, 50 SOL
        holdings = [
            {"coin_id": "bitcoin", "quantity": 0.5},
            {"coin_id": "ethereum", "quantity": 2.0},
            {"coin_id": "solana", "quantity": 50.0},
        ]

    price_map = {coin["id"]: coin for coin in prices}

    holdings_detail = []
    total_value = 0.0
    total_previous_value = 0.0

    for holding in holdings:
        coin = price_map.get(holding["coin_id"])
        if not coin:
            continue

        current_price = coin["current_price"]
        quantity = holding["quantity"]
        value = current_price * quantity

        pct_change = coin["price_change_24h"]  # e.g. -2.5 means down 2.5%

        # BUG #1: Wrong formula for recovering the previous price.
        #
        # CoinGecko's price_change_percentage_24h means:
        #   current_price = previous_price * (1 + pct_change / 100)
        #
        #
        # The code below uses subtraction instead of division:
        #   previous_price = current_price * (1 - pct_change / 100)   ← BUG
        #
        # This produces wrong magnitudes for all inputs. The degenerate case
        # pct_change = 100 gives previous_price = 0, causing division-by-zero
        # in the portfolio percentage calculation below.
        previous_price = current_price * (1 - pct_change / 100)  # BUG #1
        previous_value = previous_price * quantity

        total_value += value
        total_previous_value += previous_value

        holdings_detail.append({
            "coin_id": holding["coin_id"],
            "symbol": coin["symbol"],
            "name": coin["name"],
            "quantity": quantity,
            "current_price": current_price,
            "value_usd": value,
            "price_change_24h_pct": pct_change,
        })

    if total_previous_value > 0:
        total_change_24h_pct = (
            (total_value - total_previous_value) / total_previous_value
        ) * 100
    else:
        total_change_24h_pct = 0.0

    return {
        "total_value_usd": round(total_value, 2),
        "holdings_detail": holdings_detail,
        "total_change_24h_pct": round(total_change_24h_pct, 4),
    }
