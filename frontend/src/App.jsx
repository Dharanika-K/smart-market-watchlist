import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [watchlists, setWatchlists] = useState([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState(null);
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newStock, setNewStock] = useState("");
  const [newWatchlist, setNewWatchlist] = useState("");
  const [toast, setToast] = useState("");
  // Load watchlists
  const loadWatchlists = async () => {
    try {
      const response = await axios.get(`${API}/watchlists`);
      setWatchlists(response.data);

      if (response.data.length > 0 && !selectedWatchlist) {
        setSelectedWatchlist(response.data[0]);
      }
    } catch (error) {
      console.error("Failed to load watchlists:", error);
    }
  };

  // Load market changes
  const loadChanges = async (watchlistId) => {
    if (!watchlistId) return;

    setLoading(true);

    try {
      const response = await axios.get(
        `${API}/watchlists/${watchlistId}/changes`
      );

      setChanges(response.data);
    } catch (error) {
      console.error("Failed to load changes:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWatchlists();
  }, []);

  useEffect(() => {
    if (selectedWatchlist) {
      loadChanges(selectedWatchlist.id);
    }
  }, [selectedWatchlist]);

  // Create watchlist
  const createWatchlist = async () => {
    if (!newWatchlist.trim()) return;

    try {
      const response = await axios.post(`${API}/watchlists`, {
        name: newWatchlist,
      });

      setWatchlists([...watchlists, response.data]);
      setSelectedWatchlist(response.data);
      setNewWatchlist("");
    } catch (error) {
      console.error("Failed to create watchlist:", error);
    }
  };

  // Add stock
  const addStock = async () => {
    if (!newStock.trim() || !selectedWatchlist) return;

    try {
      await axios.post(
        `${API}/watchlists/${selectedWatchlist.id}/stocks`,
        {
          symbol: newStock.toUpperCase(),
        }
      );

      setNewStock("");

      // Refresh watchlist
      const response = await axios.get(`${API}/watchlists`);

      setWatchlists(response.data);

      const updated = response.data.find(
        (item) => item.id === selectedWatchlist.id
      );

      setSelectedWatchlist(updated);

      loadChanges(updated.id);
    } catch (error) {
      console.error("Failed to add stock:", error);
      alert("Unable to add stock. Check the stock symbol.");
    }
  };

  // Mark stock as checked
  const markChecked = async (symbol) => {
    try {
      await axios.post(
        `${API}/watchlists/${selectedWatchlist.id}/stocks/${symbol}/check`
      );

      loadChanges(selectedWatchlist.id);
    } catch (error) {
      console.error("Failed to mark stock:", error);
    }
  };
const removeStock = async (symbol) => {
  if (!selectedWatchlist) return;

  try {
    await axios.delete(
      `${API}/watchlists/${selectedWatchlist.id}/stocks/${symbol}`
    );

    const response = await axios.get(`${API}/watchlists`);

    setWatchlists(response.data);

    const updated = response.data.find(
      (item) => item.id === selectedWatchlist.id
    );

    setSelectedWatchlist(updated);

    loadChanges(updated.id);

    // Show success notification
    setToast(`✓ ${symbol} removed from watchlist`);

    // Automatically hide after 3 seconds
    setTimeout(() => {
      setToast("");
    }, 3000);

  } catch (error) {
    console.error("Failed to remove stock:", error);

    setToast("⚠ Unable to remove stock");

    setTimeout(() => {
      setToast("");
    }, 3000);
  }
};

  const getSeverityClass = (severity) => {
    if (severity === "HIGH") return "high";
    if (severity === "MEDIUM") return "medium";
    if (severity === "LOW") return "low";
    return "normal";
  };

  return (
    <div className="app">
      {toast && (
  <div className="toast">
    {toast}
  </div>
)}
      {/* Header */}
      <header className="header">
        <div>
          <h1>📈 Smart Market Watchlist</h1>
          <p>Know what changed since you last checked.</p>
        </div>

        <button
          className="refresh-btn"
          onClick={() =>
            selectedWatchlist && loadChanges(selectedWatchlist.id)
          }
        >
          🔄 Refresh
        </button>
      </header>

      <main className="container">
        {/* Watchlist selector */}
        <section className="watchlist-bar">
          <div>
            <label>Watchlist</label>

            <select
              value={selectedWatchlist?.id || ""}
              onChange={(e) => {
                const selected = watchlists.find(
                  (item) => item.id === e.target.value
                );

                setSelectedWatchlist(selected);
              }}
            >
              {watchlists.map((watchlist) => (
                <option key={watchlist.id} value={watchlist.id}>
                  {watchlist.name}
                </option>
              ))}
            </select>
          </div>

          <div className="create-watchlist">
            <input
              value={newWatchlist}
              onChange={(e) => setNewWatchlist(e.target.value)}
              placeholder="New watchlist name"
            />

            <button onClick={createWatchlist}>
              + Create
            </button>
          </div>
        </section>

        {/* Add stock */}
        <section className="add-stock">
          <input
            value={newStock}
            onChange={(e) => setNewStock(e.target.value)}
            placeholder="Enter stock symbol e.g. AAPL"
            onKeyDown={(e) => {
              if (e.key === "Enter") addStock();
            }}
          />

          <button onClick={addStock}>
            + Add Stock
          </button>
        </section>

        {/* Summary */}
        <section className="summary">
          <div>
            <span>Total Stocks</span>
            <strong>{changes.length}</strong>
          </div>

          <div>
            <span>High Impact</span>
            <strong>
              {changes.filter((item) => item.severity === "HIGH").length}
            </strong>
          </div>

          <div>
            <span>Needs Attention</span>
            <strong>
              {
                changes.filter(
                  (item) =>
                    item.severity === "HIGH" ||
                    item.severity === "MEDIUM"
                ).length
              }
            </strong>
          </div>
        </section>

        {/* Market cards */}
        <section className="market-section">
          <div className="section-title">
            <div>
              <h2>Since you last checked</h2>
              <p>
                Changes are ranked using price movement and unusual volume.
              </p>
            </div>
          </div>

          {loading ? (
            <div className="loading">Loading market data...</div>
          ) : changes.length === 0 ? (
            <div className="empty">
              <h3>Your watchlist is empty</h3>
              <p>Add a stock above to start monitoring the market.</p>
            </div>
          ) : (
            <div className="cards">
              {changes.map((item) => (
                <div
                  className={`stock-card ${getSeverityClass(
                    item.severity
                  )}`}
                  key={item.symbol}
                >
                  <div className="card-top">
                    <div>
                      <h3>{item.symbol}</h3>
                      <span className="severity">
                        {item.severity}
                      </span>
                    </div>

                    <div className="score">
                      <span>Change Score</span>
                      <strong>{item.change_score}/100</strong>
                    </div>
                  </div>

                  {item.error ? (
                    <div className="error">
                      Unable to retrieve market data.
                    </div>
                  ) : (
                    <>
                      <div className="price-row">
                        <div>
                          <span>Current Price</span>
                          <strong>
                            ${item.current_price?.toFixed(2)}
                          </strong>
                        </div>

                        <div
                          className={
                            item.price_change_percent > 0
                              ? "positive"
                              : item.price_change_percent < 0
                              ? "negative"
                              : "neutral"
                          }
                        >
                          {item.price_change_percent > 0
                            ? "▲"
                            : item.price_change_percent < 0
                            ? "▼"
                            : "—"}{" "}
                          {Math.abs(
                            item.price_change_percent
                          ).toFixed(2)}
                          %
                        </div>
                      </div>

                      <div className="metrics">
                        <div>
                          <span>Volume</span>
                          <strong>
                            {(
                              item.current_volume / 1000000
                            ).toFixed(1)}
                            M
                          </strong>
                        </div>

                        <div>
                          <span>Volume vs Normal</span>
                          <strong>
                            {item.volume_ratio?.toFixed(2)}×
                          </strong>
                        </div>
                      </div>

                      <div className="reasons">
                        <h4>Why this matters</h4>

                        {item.reasons?.length > 0 ? (
                          <ul>
                            {item.reasons.map((reason, index) => (
                              <li key={index}>{reason}</li>
                            ))}
                          </ul>
                        ) : (
                          <p>No meaningful changes detected.</p>
                        )}
                      </div>

                      <div className="card-actions">
                      <button
                        className="check-btn"
                        onClick={() => markChecked(item.symbol)}
                      >
                        ✓ Mark as Checked
                      </button>

                      <button
                        className="remove-btn"
                        onClick={() => removeStock(item.symbol)}
                      >
                        Remove
                      </button>
                    </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Footer status */}
        <footer>
          <span>🟢 Market data available</span>
          <span>Smart change detection enabled</span>
        </footer>
      </main>
    </div>
  );
}

export default App;