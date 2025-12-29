"""
Market Data Service - Fetches stock data from multiple sources
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from cachetools import TTLCache
import httpx

from config import get_settings

# Cache for 1 minute
quote_cache = TTLCache(maxsize=500, ttl=60)
# Cache for 5 minutes
data_cache = TTLCache(maxsize=100, ttl=300)


class MarketDataService:
    """Service for fetching market data from various sources"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol"""
        cache_key = f"quote_{symbol}"
        if cache_key in quote_cache:
            return quote_cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            quote = {
                "symbol": symbol.upper(),
                "name": info.get("shortName", info.get("longName", symbol)),
                "price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
                "change": info.get("regularMarketChange", 0),
                "changePercent": info.get("regularMarketChangePercent", 0),
                "open": info.get("regularMarketOpen", 0),
                "high": info.get("regularMarketDayHigh", 0),
                "low": info.get("regularMarketDayLow", 0),
                "volume": info.get("regularMarketVolume", 0),
                "avgVolume": info.get("averageVolume", 0),
                "marketCap": info.get("marketCap", 0),
                "peRatio": info.get("trailingPE", 0),
                "eps": info.get("trailingEps", 0),
                "week52High": info.get("fiftyTwoWeekHigh", 0),
                "week52Low": info.get("fiftyTwoWeekLow", 0),
                "dividend": info.get("dividendYield", 0),
                "beta": info.get("beta", 0),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "exchange": info.get("exchange", ""),
                "currency": info.get("currency", "USD"),
                "timestamp": datetime.now().isoformat()
            }
            
            quote_cache[cache_key] = quote
            return quote
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1mo",
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """Get historical OHLCV data"""
        cache_key = f"hist_{symbol}_{period}_{interval}"
        if cache_key in data_cache:
            return data_cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            data = []
            for index, row in df.iterrows():
                data.append({
                    "timestamp": int(index.timestamp() * 1000),
                    "date": index.strftime("%Y-%m-%d %H:%M"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })
            
            data_cache[cache_key] = data
            return data
        except Exception as e:
            return []
    
    async def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol.upper(),
                "name": info.get("longName", ""),
                "description": info.get("longBusinessSummary", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "website": info.get("website", ""),
                "employees": info.get("fullTimeEmployees", 0),
                "headquarters": f"{info.get('city', '')}, {info.get('country', '')}",
                "ceo": info.get("companyOfficers", [{}])[0].get("name", "") if info.get("companyOfficers") else "",
                "founded": info.get("founded", ""),
                "marketCap": info.get("marketCap", 0),
                "enterpriseValue": info.get("enterpriseValue", 0),
                "revenue": info.get("totalRevenue", 0),
                "grossProfit": info.get("grossProfits", 0),
                "ebitda": info.get("ebitda", 0),
                "netIncome": info.get("netIncomeToCommon", 0),
                "debtToEquity": info.get("debtToEquity", 0),
                "returnOnEquity": info.get("returnOnEquity", 0),
                "returnOnAssets": info.get("returnOnAssets", 0),
                "profitMargin": info.get("profitMargins", 0),
                "operatingMargin": info.get("operatingMargins", 0)
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
    
    async def get_financials(self, symbol: str) -> Dict[str, Any]:
        """Get financial statements"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get income statement, balance sheet, cash flow
            income = ticker.income_stmt
            balance = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            def df_to_dict(df):
                if df is None or df.empty:
                    return {}
                result = {}
                for col in df.columns:
                    result[col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col)] = {
                        k: float(v) if v == v else 0 for k, v in df[col].to_dict().items()
                    }
                return result
            
            return {
                "symbol": symbol.upper(),
                "incomeStatement": df_to_dict(income),
                "balanceSheet": df_to_dict(balance),
                "cashFlow": df_to_dict(cashflow)
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
    
    async def get_market_indices(self) -> List[Dict[str, Any]]:
        """Get major market indices"""
        indices = [
            ("^GSPC", "S&P 500"),
            ("^DJI", "Dow Jones"),
            ("^IXIC", "NASDAQ"),
            ("^RUT", "Russell 2000"),
            ("^VIX", "VIX"),
            ("^FTSE", "FTSE 100"),
            ("^N225", "Nikkei 225"),
        ]
        
        results = []
        for symbol, name in indices:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "price": info.get("regularMarketPrice", 0),
                    "change": info.get("regularMarketChange", 0),
                    "changePercent": info.get("regularMarketChangePercent", 0)
                })
            except:
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "price": 0,
                    "change": 0,
                    "changePercent": 0
                })
        
        return results
    
    async def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols by name or ticker"""
        try:
            # Use yfinance's search functionality
            tickers = yf.Tickers(query)
            results = []
            
            # Also try direct lookup
            try:
                ticker = yf.Ticker(query)
                info = ticker.info
                if info.get("symbol"):
                    results.append({
                        "symbol": info.get("symbol", query.upper()),
                        "name": info.get("shortName", ""),
                        "exchange": info.get("exchange", ""),
                        "type": info.get("quoteType", "")
                    })
            except:
                pass
            
            return results
        except Exception as e:
            return []
    
    async def get_sector_performance(self) -> List[Dict[str, Any]]:
        """Get sector ETF performance as proxy for sectors"""
        sector_etfs = [
            ("XLK", "Technology"),
            ("XLF", "Financials"),
            ("XLV", "Healthcare"),
            ("XLE", "Energy"),
            ("XLI", "Industrials"),
            ("XLP", "Consumer Staples"),
            ("XLY", "Consumer Discretionary"),
            ("XLU", "Utilities"),
            ("XLRE", "Real Estate"),
            ("XLB", "Materials"),
            ("XLC", "Communication Services")
        ]
        
        results = []
        for symbol, sector in sector_etfs:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                results.append({
                    "symbol": symbol,
                    "sector": sector,
                    "price": info.get("regularMarketPrice", 0),
                    "change": info.get("regularMarketChange", 0),
                    "changePercent": info.get("regularMarketChangePercent", 0)
                })
            except:
                pass
        
        return results


# Singleton instance
market_service = MarketDataService()
