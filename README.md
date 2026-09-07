# 📊 Bloomberg Terminal Alternative

A full-stack, enterprise-grade financial analytics and market intelligence terminal built with **Angular 17** and **Python FastAPI**. Features real-time market data streaming, technical indicators, and AI-powered market analysis via Gemini.

![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Angular](https://img.shields.io/badge/Angular-17-dd0031?logo=angular&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini-AI-4285F4?logo=google&logoColor=white)

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 ANGULAR 17 PRESENTATION LAYER               │
│  Bloomberg Dark Theme · Highcharts/TradingView · RxJS State │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FASTAPI ASYNCHRONOUS BACKEND                │
│   Routers: Market · Analysis · News · Portfolio · Screener  │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│    MARKET DATA ENGINE       │ │       AI ANALYST ENGINE     │
│ Yahoo Finance · SQLite DB   │ │ Gemini LLM · Sentiment RAG  │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

## 🚀 Key Features

- **📈 Real-Time Market Overview**: Live equity prices, intraday candle charts, and sector heatmaps.
- **🧠 AI Equity Analyst**: Deep conversational insights, automated balance-sheet summarization, and valuation analysis powered by Google Gemini.
- **📐 Technical Indicator Suite**: Real-time calculation of RSI, MACD, Bollinger Bands, and Moving Averages (SMA/EMA).
- **📰 Sentiment News Screener**: Real-time aggregation of market headlines classified by sentiment (Bullish / Bearish / Neutral).
- **💼 Portfolio & Watchlist Manager**: Real-time P&L tracking, risk metrics, and custom asset allocations.

---

## 🛠️ Project Structure

```
bloomberg_terminal/
├── backend/
│   ├── database/             # SQLite connection & schema models
│   ├── routers/              # Modular API route controllers
│   │   ├── analysis.py       # AI analysis endpoints
│   │   ├── market.py         # Real-time quotes & historical data
│   │   ├── news.py           # Headline aggregator
│   │   ├── portfolio.py      # User portfolio state
│   │   └── screener.py       # Stock filter & technical scanners
│   ├── services/             # Core business logic & LLM integrations
│   │   ├── llm_service.py    # Gemini AI analyst service
│   │   ├── market_data.py    # Yahoo Finance & data fetcher
│   │   └── technical.py      # Technical indicator calculators
│   ├── config.py             # Typed application settings
│   └── main.py               # FastAPI application entrypoint
├── src/                      # Angular 17 frontend
│   ├── app/
│   │   ├── pages/            # Feature pages (Dashboard, Screener, Portfolio, etc.)
│   │   └── services/         # Angular HTTP & WebSocket services
│   └── styles.scss           # Bloomberg terminal dark theme
└── AGENTS.md                 # Autonomous engineering directives
```

---

## ⚙️ Quickstart Guide

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your GEMINI_API_KEY (optional)
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup (Angular)
```bash
npm install
npm run start
```
Open `http://localhost:4200` to view the terminal.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/market/quote/{symbol}` | Fetch real-time price quote and daily range |
| `GET` | `/api/market/history/{symbol}` | Historical OHLCV candle data |
| `POST` | `/api/analysis/query` | Ask AI Analyst questions regarding ticker or sector |
| `GET` | `/api/news/headlines` | Latest financial headlines with sentiment scores |
| `GET` | `/api/screener/scan` | Filter equities by P/E, Market Cap, and RSI |
