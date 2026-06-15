import React, { useState, useEffect, useCallback, useMemo } from "react";
import CryptoCard from "./CryptoCard";

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

function buildDefaultInterval(): number {
  const stored = typeof window !== "undefined" ? window.localStorage.getItem("refreshInterval") : null;
  const parsed = stored ? Number(stored) : NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 30000;
}

export default function PriceTable() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const [refreshInterval, setRefreshInterval] = useState(buildDefaultInterval());

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        const r = await fetch("/api/prices");
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const body: { data: Coin[] } = await r.json();
        if (cancelled) return;

        setCoins(body.data);
        setError(null);
      } catch (e) {
        if (cancelled) return;
        setError((e as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchData();

    const interval = setInterval(fetchData, refreshInterval);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const filterCoins = useCallback(
    (q: string) => {
      const needle = q.trim().toLowerCase();
      if (!needle) return coins;
      return coins.filter((c) => c.name.toLowerCase().includes(needle) || c.symbol.toLowerCase().includes(needle));
    },
    [coins]
  );

  const visibleCoins = useMemo(() => filterCoins(query), [query, filterCoins]);

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-gray-800 rounded-xl px-5 py-4 h-16 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="text-center py-12 text-red-400 text-sm">Failed to load prices: {error}</div>;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-500">Refreshing every {refreshInterval / 1000}s</span>
        <select
          className="bg-gray-800 text-gray-300 text-xs rounded px-2 py-1 border border-gray-700"
          value={refreshInterval}
          onChange={(e) => setRefreshInterval(Number(e.target.value))}>
          <option value={5000}>5s</option>
          <option value={15000}>15s</option>
          <option value={30000}>30s</option>
          <option value={60000}>60s</option>
        </select>
      </div>

      <input
        type="text"
        placeholder="Search coins…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full bg-gray-800 text-gray-200 text-sm rounded-lg px-3 py-2 border border-gray-700 focus:outline-none focus:border-indigo-500"
      />

      {visibleCoins.length === 0 ? (
        <div className="text-center text-gray-500 text-sm py-8">No coins match “{query}”.</div>
      ) : (
        visibleCoins.map((coin) => <CryptoCard key={coin.id} coin={coin} />)
      )}
    </div>
  );
}
