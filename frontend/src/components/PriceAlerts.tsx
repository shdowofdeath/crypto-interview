import React, { useState, useEffect } from "react";
import clsx from "clsx";

type AlertCondition = "above" | "below";

interface PriceAlert {
  id: string;
  coin_id: string;
  symbol: string;
  condition: AlertCondition;
  target_price: number;
  current_price: number;
  created_at: string;
}

interface AlertsResponse {
  data: PriceAlert[];
}

function formatCurrency(value: number): string {
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function PriceAlerts() {
  const [data, setData] = useState<AlertsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/alerts")
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
      <div className="bg-indigo-950/40 border-b border-indigo-900/60 px-6 py-3">
        <div className="max-w-4xl mx-auto animate-pulse">
          <div className="h-3 bg-indigo-900/60 rounded w-32 mb-2" />
          <div className="h-4 bg-indigo-900/60 rounded w-64" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 border-b border-red-900/60 px-6 py-2">
        <p className="max-w-4xl mx-auto text-xs text-red-400">
          Price alerts unavailable: {error}
        </p>
      </div>
    );
  }

  if (!data || data.data.length === 0) return null;

  return (
    <div className="bg-indigo-950/40 border-b border-indigo-900/60 px-6 py-3">
      <div className="max-w-4xl mx-auto">
        <p className="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-1">
          🔔 Price Alerts ({data.data.length})
        </p>
        <div className="flex flex-wrap gap-x-6 gap-y-1">
          {data.data.map((alert) => {
            const triggered =
              alert.condition === "above"
                ? alert.current_price >= alert.target_price
                : alert.current_price <= alert.target_price;
            const symbol = alert.condition === "above" ? ">" : "<";

            return (
              <p
                key={alert.id}
                className={clsx(
                  "text-sm font-mono",
                  triggered ? "text-amber-400" : "text-gray-300"
                )}
              >
                {alert.symbol} {symbol} {formatCurrency(alert.target_price)}
                <span className="text-gray-500">
                  {" "}
                  · now {formatCurrency(alert.current_price)}
                </span>
                {triggered && <span className="ml-1">●</span>}
              </p>
            );
          })}
        </div>
      </div>
    </div>
  );
}
