# 📊 Bloomberg Terminal Alternative

A comprehensive financial terminal application built with Angular 17 and Python FastAPI, featuring real-time market data, AI-powered analysis using Gemini, and a Bloomberg-style dark UI.

![Bloomberg Terminal Alternative](https://img.shields.io/badge/version-1.0.0-orange) ![Angular](https://img.shields.io/badge/Angular-17-dd0031) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688) ![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4)

## ✨ Features

### 📈 Market Data
- Real-time stock quotes via yfinance (no API key required)
- Major market indices (S&P 500, NASDAQ, Dow Jones, etc.)
- Historical OHLCV data with multiple timeframes
- Sector performance heatmap

### 📊 Technical Analysis
- RSI, MACD, Bollinger Bands
- Moving averages (SMA 20/50/200, EMA)
- ATR (Average True Range)
- Trading signals detection

### 🤖 AI Analyst (Gemini)
- Natural language stock analysis
- Company comparisons
- News summarization
- Interactive chat interface

### 📰 News Feed
- Real-time financial news
- Sentiment analysis
- AI-generated summaries

### 💼 Portfolio Management
- Track holdings with P&L
- Cost basis and gains calculation
- Multiple watchlists

### 🔍 Stock Screener
- Custom filters (market cap, P/E, dividend, sector)
- Pre-built screens (gainers, losers, value, dividend)
- Most active stocks

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.10+
- Gemini API key (optional, for AI features)

### Installation

1. **Clone and install frontend dependencies:**
```bash
cd bloomberg_terminal
npm install
```

2. **Install backend dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Edit backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Run the application:**

**Option A - Run separately:**
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
npm start
```

**Option B - Run together:**
```bash
npm run dev
```

5. **Open the app:**
- Frontend: http://localhost:4200
- API Docs: http://localhost:8000/docs

## 🎨 UI Features

- **Bloomberg-style dark theme** with orange accents
- **Command bar** for quick symbol lookup
- **Keyboard navigation** (Enter to search)
- **Real-time market status** indicator
- **Responsive grid layout**

## 🔧 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/market/quote/{symbol}` | Get stock quote |
| `GET /api/market/history/{symbol}` | Historical data |
| `GET /api/market/indices` | Market indices |
| `GET /api/market/technical/{symbol}` | Technical indicators |
| `GET /api/news/` | Financial news |
| `POST /api/analysis/chat` | AI chat |
| `GET /api/analysis/stock/{symbol}` | AI stock analysis |
| `GET /api/portfolio/{id}` | Portfolio holdings |
| `GET /api/watchlist/{id}` | Watchlist items |
| `POST /api/screener/screen` | Custom stock screen |

## 📁 Project Structure

```
bloomberg_terminal/
├── src/                          # Angular frontend
│   ├── app/
│   │   ├── pages/               # Page components
│   │   │   ├── dashboard/       # Main dashboard
│   │   │   ├── stock-detail/    # Stock details & analysis
│   │   │   ├── news/            # News feed
│   │   │   ├── portfolio/       # Portfolio management
│   │   │   ├── screener/        # Stock screener
│   │   │   └── ai-analyst/      # AI chat
│   │   └── services/            # API service
│   └── styles.scss              # Global Bloomberg theme
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── routers/                 # API routes
│   ├── services/                # Business logic
│   │   ├── market_data.py       # yfinance integration
│   │   ├── llm_service.py       # Gemini AI
│   │   ├── news_service.py      # News aggregation
│   │   └── technical.py         # TA indicators
│   └── database/                # SQLite for persistence
└── package.json
```

## 🔮 Future Enhancements

- [ ] WebSocket for real-time price updates
- [ ] TradingView charts integration
- [ ] Options chain data
- [ ] Economic calendar
- [ ] Alert notifications
- [ ] Export to Excel
- [ ] Multi-currency support

## ⚠️ Disclaimer

This is an educational project. The data and analysis provided should not be used for actual trading decisions. Always consult a licensed financial advisor for investment advice.

## 📄 License

MIT License
