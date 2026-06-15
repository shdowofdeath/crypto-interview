import React from "react";
import PriceTable from "./components/PriceTable";
import PortfolioSummary from "./components/PortfolioSummary";
import PriceAlerts from "./components/PriceAlerts";

function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold text-indigo-400">CryptoWatch</h1>
        <p className="text-sm text-gray-400 mt-1">
          Live prices · Portfolio tracker
        </p>
      </header>

      <PriceAlerts />

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-10">
        <PortfolioSummary />
        <section>
          <h2 className="text-lg font-semibold text-gray-200 mb-4">
            Market Prices
          </h2>
          <PriceTable />
        </section>
      </main>
    </div>
  );
}

export default App;
