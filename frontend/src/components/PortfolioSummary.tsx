import React, { useState, useEffect } from "react";
import clsx from "clsx";

interface PortfolioData {
  total_value_usd: number;
  total_change_24h_pct: number;
  holdings_detail: Array<{
    coin_id: string;
    symbol: string;
    name: string;
    quantity: number;
    current_price: number;
    value_usd: number;
    price_change_24h_pct: number;
  }>;
}

export default function PortfolioSummary() {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/portfolio")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-2xl p-6 animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-32 mb-3" />
        <div className="h-10 bg-gray-700 rounded w-48" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-2xl p-6 border border-red-800">
        <p className="text-red-400 text-sm">Portfolio unavailable: {error}</p>
      </div>
    );
  }

  if (!data) return null;

  const isPositive = data.total_change_24h_pct >= 0;

  return (
    <section className="bg-gray-800 rounded-2xl p-6">
      <h2 className="text-sm text-gray-400 uppercase tracking-wide mb-1">
        Portfolio Value
      </h2>
      <div className="flex items-end gap-4 mb-6">
        <span className="text-4xl font-bold">
          ${data.total_value_usd.toLocaleString()}
        </span>
        <span
          className={clsx(
            "text-lg font-semibold mb-1",
            isPositive ? "text-green-400" : "text-red-400"
          )}
        >
          {isPositive ? "+" : ""}
          {data.total_change_24h_pct.toFixed(2)}% today
        </span>
      </div>

      <div className="space-y-2">
        {data.holdings_detail.map((h) => (
          <div
            key={h.coin_id}
            className="flex justify-between text-sm text-gray-300"
          >
            <span>
              {h.quantity} {h.symbol}
            </span>
            <span>${h.value_usd.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
