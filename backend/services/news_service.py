"""
News Service - Fetches financial news from various sources
"""
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from cachetools import TTLCache
import yfinance as yf

from config import get_settings

# Cache for 5 minutes
news_cache = TTLCache(maxsize=100, ttl=300)


class NewsService:
    """Service for fetching financial news"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def get_news(self, symbol: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get news for a specific symbol or general market news"""
        cache_key = f"news_{symbol or 'general'}_{limit}"
        if cache_key in news_cache:
            return news_cache[cache_key]
        
        news_items = []
        
        try:
            if symbol:
                # Get company-specific news from yfinance
                ticker = yf.Ticker(symbol)
                news = ticker.news
                
                for item in news[:limit]:
                    news_items.append({
                        "id": item.get("uuid", ""),
                        "title": item.get("title", ""),
                        "summary": item.get("summary", ""),
                        "source": item.get("publisher", ""),
                        "url": item.get("link", ""),
                        "publishedAt": datetime.fromtimestamp(
                            item.get("providerPublishTime", 0)
                        ).isoformat() if item.get("providerPublishTime") else "",
                        "thumbnail": item.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "") if item.get("thumbnail") else "",
                        "symbol": symbol.upper(),
                        "sentiment": self._analyze_sentiment(item.get("title", ""))
                    })
            else:
                # Get general market news for major indices
                symbols = ["SPY", "QQQ", "DIA"]
                seen_ids = set()
                
                for sym in symbols:
                    try:
                        ticker = yf.Ticker(sym)
                        news = ticker.news
                        
                        for item in news[:10]:
                            item_id = item.get("uuid", "")
                            if item_id not in seen_ids:
                                seen_ids.add(item_id)
                                news_items.append({
                                    "id": item_id,
                                    "title": item.get("title", ""),
                                    "summary": item.get("summary", ""),
                                    "source": item.get("publisher", ""),
                                    "url": item.get("link", ""),
                                    "publishedAt": datetime.fromtimestamp(
                                        item.get("providerPublishTime", 0)
                                    ).isoformat() if item.get("providerPublishTime") else "",
                                    "thumbnail": item.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "") if item.get("thumbnail") else "",
                                    "symbol": sym,
                                    "sentiment": self._analyze_sentiment(item.get("title", ""))
                                })
                    except:
                        pass
                
                # Sort by publish date
                news_items.sort(
                    key=lambda x: x.get("publishedAt", ""), 
                    reverse=True
                )
                news_items = news_items[:limit]
        
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        news_cache[cache_key] = news_items
        return news_items
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on keywords"""
        text_lower = text.lower()
        
        positive_words = [
            "surge", "soar", "jump", "gain", "rise", "rally", "bullish",
            "beat", "exceed", "record", "high", "growth", "profit", "buy",
            "upgrade", "strong", "positive", "boom", "success"
        ]
        
        negative_words = [
            "fall", "drop", "plunge", "crash", "decline", "bearish", "sell",
            "miss", "loss", "low", "weak", "negative", "downgrade", "cut",
            "warning", "concern", "fear", "crisis", "recession"
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"


# Singleton instance
news_service = NewsService()
