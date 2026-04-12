from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.coingecko import fetch_prices
from models.portfolio import compute_portfolio_value

app = FastAPI(title="CryptoWatch API")

# BUG #4: CORS is configured with a wildcard origin AND allow_credentials=True.
#
# Per the CORS specification, a server CANNOT respond with both:
#   Access-Control-Allow-Origin: *
#   Access-Control-Allow-Credentials: true
#
# Browsers reject this combination outright — credentialed requests will fail
# in every browser. Beyond the spec violation, allowing all origins (*) means
# any website on the internet can make requests to this API.
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # BUG #4: wildcard
    allow_credentials=True,   # BUG #4: invalid with wildcard per CORS spec
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/prices")
async def get_prices():
    """Return current prices for tracked coins."""
    # Note: fetch_prices() is synchronous — see bug #3 in services/coingecko.py
    try:
        prices = fetch_prices()
        return {"data": prices}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")


@app.get("/api/portfolio")
async def get_portfolio():
    """Return portfolio value and 24h change for the demo holdings."""
    try:
        prices = fetch_prices()
        result = compute_portfolio_value(prices)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
