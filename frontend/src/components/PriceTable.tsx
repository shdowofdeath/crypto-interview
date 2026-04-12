import React, { useState, useEffect } from "react";
import CryptoCard from "./CryptoCard";

// BUG #5: Hardcoded mock data — this component never calls the backend API.
// The `coins` state is seeded with MOCK_DATA and fetchData() is a no-op.
//
//
// Reference: PortfolioSummary.tsx shows the correct pattern.
const MOCK_DATA = [
  {
    id: "bitcoin",
    symbol: "BTC",
    name: "Bitcoin",
    current_price: 62000,
    price_change_24h: 2.4,
    market_cap: 1220000000000,
    image: "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
    last_updated: "2024-01-01T00:00:00.000Z",
  },
  {
    id: "ethereum",
    symbol: "ETH",
    name: "Ethereum",
    current_price: 3100,
    price_change_24h: -1.8,
    market_cap: 373000000000,
    image: "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
    last_updated: "2024-01-01T00:00:00.000Z",
  },
  {
    id: "solana",
    symbol: "SOL",
    name: "Solana",
    current_price: 145,
    price_change_24h: 5.1,
    market_cap: 67000000000,
    image: "https://assets.coingecko.com/coins/images/4128/small/solana.png",
    last_updated: "2024-01-01T00:00:00.000Z",
  },
  {
    id: "cardano",
    symbol: "ADA",
    name: "Cardano",
    current_price: 0.45,
    price_change_24h: -0.9,
    market_cap: 16000000000,
    image: "https://assets.coingecko.com/coins/images/975/small/cardano.png",
    last_updated: "2024-01-01T00:00:00.000Z",
  },
  {
    id: "polkadot",
    symbol: "DOT",
    name: "Polkadot",
    current_price: 7.2,
    price_change_24h: 1.3,
    market_cap: 10000000000,
    image: "https://assets.coingecko.com/coins/images/12171/small/polkadot.png",
    last_updated: "2024-01-01T00:00:00.000Z",
  },
];

interface Coin {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_24h: number;
  market_cap: number;
  image: string;
  last_updated: string;
}

export default function PriceTable() {
  const [coins, setCoins] = useState<Coin[]>(MOCK_DATA); // BUG #5: seeded with mock data
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // BUG #6: `refreshInterval` controls how often prices refresh.
  // When the user changes the dropdown, the interval should update immediately.
  // But because `refreshInterval` is missing from the useEffect dependency array,
  // the setInterval captures the initial value (30000ms) and never re-subscribes.
  // Changing the dropdown has no effect on the actual polling frequency.
  const [refreshInterval, setRefreshInterval] = useState(30000);

  useEffect(() => {
    const fetchData = async () => {
      // BUG #5: fetchData does nothing — it should call /api/prices
      // and update the `coins` state with the response.
      setLoading(false);
    };

    fetchData();

    // BUG #6: `refreshInterval` is captured from the closure at the time
    // this effect ran (initial render = 30000ms). The interval never
    // updates because this effect never re-runs — refreshInterval is
    // missing from the dependency array below.
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // BUG #6: should be [refreshInterval]

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="bg-gray-800 rounded-xl px-5 py-4 h-16 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-400 text-sm">
        Failed to load prices: {error}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-500">
          Refreshing every {refreshInterval / 1000}s
        </span>
        <select
          className="bg-gray-800 text-gray-300 text-xs rounded px-2 py-1 border border-gray-700"
          value={refreshInterval}
          onChange={(e) => setRefreshInterval(Number(e.target.value))}
        >
          <option value={5000}>5s</option>
          <option value={15000}>15s</option>
          <option value={30000}>30s</option>
          <option value={60000}>60s</option>
        </select>
      </div>

      {coins.map((coin) => (
        <CryptoCard key={coin.id} coin={coin} />
      ))}
    </div>
  );
}
