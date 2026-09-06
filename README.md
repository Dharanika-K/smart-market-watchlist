# 📈 Smart Market Watchlist

> **Know what changed since you last checked.**

Smart Market Watchlist is an intelligent market-monitoring web application that helps users understand **meaningful changes in their stock watchlist** instead of simply displaying stock prices.

The system analyzes price movement, trading volume, and market signals to generate an explainable **change score** and prioritize stocks that need attention.

---

## 🚀 Problem

Traditional stock watchlists mainly show:

- Current price
- Price change
- Trading volume

This still requires users to manually scan every stock and determine what actually matters.

### Our solution

Smart Market Watchlist answers:

> **What changed, how significant is it, and why should I pay attention?**

The dashboard ranks stocks according to the significance of their recent market changes and explains the reasons behind the ranking.

---

## ✨ Features

### 📋 Personalized Watchlists
- Create multiple watchlists
- Add and remove stocks
- Persistent storage using MongoDB

### 🔎 Stock Search
- Search supported stock symbols
- Add stocks directly from search suggestions
- Prevent duplicate stocks
- Validate stock symbols before adding

### 📊 Market Intelligence
For every stock, the dashboard displays:

- Current price
- Price movement percentage
- Trading volume
- Volume ratio
- Recent price trend
- Market signals
- Data freshness status

### 🧠 Change Intelligence Engine

The system calculates a change score using multiple signals:

- Price movement
- Unusual trading volume
- Market events/signals

Each stock is classified into:

| Severity | Meaning |
|----------|---------|
| 🔴 HIGH | Major change requiring attention |
| 🟠 MEDIUM | Significant market movement |
| 🔵 LOW | Smaller meaningful change |
| 🟢 NORMAL | No major change detected |

### 🎯 Priority-Based Dashboard

Stocks are ranked according to their impact so users can focus on the most important changes first.

### 🕐 Since You Last Checked

Users can mark a stock as checked.

When they return later, the application helps them focus on changes that occurred after their previous review.

### ⚠️ Resilience & Validation

The application handles:

- Invalid stock symbols
- Duplicate stocks
- Invalid watchlist IDs
- Missing market data
- API/data errors
- Data freshness states

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │     React Frontend  │
                    │                     │
                    │  Watchlist Dashboard │
                    │  Search & Charts     │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │                     │
                    │ Watchlist Service    │
                    │ Market Service       │
                    │ Change Engine        │
                    └───────┬───────┬─────┘
                            │       │
                 ┌──────────┘       └──────────┐
                 ▼                             ▼
       ┌─────────────────┐           ┌─────────────────┐
       │   MongoDB Atlas │           │  Market Data    │
       │                 │           │                 │
       │ Watchlists      │           │    yfinance     │
       │ Snapshots       │           │                 │
       │ Market Cache    │           │                 │
       └─────────────────┘           └─────────────────┘
