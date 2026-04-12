import React, { useState } from "react";
import clsx from "clsx";

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

interface Props {
  coin: Coin;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: value >= 1 ? 2 : 6,
  }).format(value);
}

function formatMarketCap(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  return `$${value.toLocaleString()}`;
}

export default function CryptoCard({ coin }: Props) {
  const [showDetails, setShowDetails] = useState(false);
  const isPositive = coin.price_change_24h >= 0;

  return (
    // BUG #8: `overflow-hidden` clips the details panel when the card expands.
    // `h-16` sets a fixed 64px height that only fits the collapsed state —
    // the expanded details panel is completely hidden by both constraints.
    //
    <div
      className="bg-gray-800 rounded-xl px-5 py-4 overflow-hidden h-16 cursor-pointer hover:bg-gray-900 transition-colors"
      onClick={() => setShowDetails((prev) => !prev)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img
            src={coin.image}
            alt={coin.name}
            className="w-8 h-8 rounded-full"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
          <div>
            <p className="font-semibold text-white text-sm">{coin.name}</p>
            <p className="text-xs text-gray-400">{coin.symbol}</p>
          </div>
        </div>

        <div className="text-right">
          <p className="font-mono font-semibold text-sm">
            {formatCurrency(coin.current_price)}
          </p>
          {/* BUG #7: Color classes are swapped.
              A positive change (price went up) shows in red — should be green.
              A negative change (price went down) shows in green — should be red. */}
          <p
            className={clsx(
              "text-xs font-mono",
              isPositive ? "text-red-400" : "text-green-400" // BUG #7: swapped
            )}
          >
            {isPositive ? "▲" : "▼"} {Math.abs(coin.price_change_24h).toFixed(2)}%
          </p>
        </div>
      </div>

      {/* BUG #8: This panel is invisible — clipped by overflow-hidden + h-16 above */}
      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-700 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Market Cap</span>
            <span className="text-white">{formatMarketCap(coin.market_cap)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">24h Change</span>
            {/* BUG #7: same swapped colors in the detail panel */}
            <span
              className={clsx(
                isPositive ? "text-red-400" : "text-green-400" // BUG #7: swapped
              )}
            >
              {isPositive ? "+" : ""}
              {coin.price_change_24h.toFixed(2)}%
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Last updated</span>
            <span className="text-gray-300 text-xs">
              {new Date(coin.last_updated).toLocaleTimeString()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
