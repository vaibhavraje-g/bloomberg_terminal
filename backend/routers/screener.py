"""
Stock Screener Router - Filter and screen stocks
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
import yfinance as yf

from services.market_data import market_service
from services.technical import technical_service

router = APIRouter()


class ScreenerCriteria(BaseModel):
    minMarketCap: Optional[float] = None
    maxMarketCap: Optional[float] = None
    minPE: Optional[float] = None
    maxPE: Optional[float] = None
    minDividendYield: Optional[float] = None
    maxDividendYield: Optional[float] = None
    minVolume: Optional[int] = None
    sector: Optional[str] = None
    oversold: Optional[bool] = None
    overbought: Optional[bool] = None


# Pre-defined popular stocks for screening
SCREENER_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "UNH", "JNJ", "XOM", "WMT", "MA", "PG", "HD", "CVX",
    "MRK", "ABBV", "LLY", "KO", "PEP", "COST", "AVGO", "TMO", "MCD",
    "ABT", "CSCO", "DHR", "ACN", "NEE", "VZ", "ADBE", "TXN", "PM",
    "WFC", "CRM", "NKE", "QCOM", "UPS", "INTC", "AMD", "HON", "LOW",
    "MS", "CAT", "ORCL", "IBM", "BA"
]


@router.get("/universe")
async def get_screener_universe():
    """Get available stocks for screening"""
    return SCREENER_UNIVERSE


@router.post("/screen")
async def screen_stocks(criteria: ScreenerCriteria):
    """Screen stocks based on criteria"""
    results = []
    
    for symbol in SCREENER_UNIVERSE:
        try:
            quote = await market_service.get_quote(symbol)
            
            if "error" in quote:
                continue
            
            # Apply filters
            passed = True
            
            # Market Cap filter
            market_cap = quote.get("marketCap", 0)
            if criteria.minMarketCap and market_cap < criteria.minMarketCap:
                passed = False
            if criteria.maxMarketCap and market_cap > criteria.maxMarketCap:
                passed = False
            
            # P/E filter
            pe = quote.get("peRatio", 0) or 0
            if criteria.minPE and pe < criteria.minPE:
                passed = False
            if criteria.maxPE and (pe > criteria.maxPE or pe == 0):
                passed = False
            
            # Dividend yield filter
            div_yield = (quote.get("dividend", 0) or 0) * 100
            if criteria.minDividendYield and div_yield < criteria.minDividendYield:
                passed = False
            if criteria.maxDividendYield and div_yield > criteria.maxDividendYield:
                passed = False
            
            # Volume filter
            volume = quote.get("volume", 0)
            if criteria.minVolume and volume < criteria.minVolume:
                passed = False
            
            # Sector filter
            if criteria.sector and quote.get("sector", "").lower() != criteria.sector.lower():
                passed = False
            
            # RSI-based filters
            if criteria.oversold or criteria.overbought:
                tech = await technical_service.get_technical_indicators(symbol)
                rsi = tech.get("indicators", {}).get("momentum", {}).get("rsi", 50)
                
                if criteria.oversold and rsi > 30:
                    passed = False
                if criteria.overbought and rsi < 70:
                    passed = False
            
            if passed:
                results.append(quote)
        
        except Exception as e:
            continue
    
    # Sort by market cap
    results.sort(key=lambda x: x.get("marketCap", 0), reverse=True)
    
    return {
        "count": len(results),
        "results": results
    }


@router.get("/gainers")
async def get_top_gainers():
    """Get top gaining stocks"""
    quotes = []
    for symbol in SCREENER_UNIVERSE:
        try:
            quote = await market_service.get_quote(symbol)
            if "error" not in quote:
                quotes.append(quote)
        except:
            continue
    
    # Sort by change percent descending
    quotes.sort(key=lambda x: x.get("changePercent", 0), reverse=True)
    return quotes[:10]


@router.get("/losers")
async def get_top_losers():
    """Get top losing stocks"""
    quotes = []
    for symbol in SCREENER_UNIVERSE:
        try:
            quote = await market_service.get_quote(symbol)
            if "error" not in quote:
                quotes.append(quote)
        except:
            continue
    
    # Sort by change percent ascending
    quotes.sort(key=lambda x: x.get("changePercent", 0))
    return quotes[:10]


@router.get("/most-active")
async def get_most_active():
    """Get most actively traded stocks"""
    quotes = []
    for symbol in SCREENER_UNIVERSE:
        try:
            quote = await market_service.get_quote(symbol)
            if "error" not in quote:
                quotes.append(quote)
        except:
            continue
    
    # Sort by volume descending
    quotes.sort(key=lambda x: x.get("volume", 0), reverse=True)
    return quotes[:10]


@router.get("/presets/{preset}")
async def get_preset_screen(preset: str):
    """Get pre-built screen results"""
    presets = {
        "value": ScreenerCriteria(maxPE=15, minDividendYield=2),
        "growth": ScreenerCriteria(minMarketCap=50000000000),
        "dividend": ScreenerCriteria(minDividendYield=3),
        "tech": ScreenerCriteria(sector="Technology"),
        "largecap": ScreenerCriteria(minMarketCap=200000000000),
        "oversold": ScreenerCriteria(oversold=True),
        "overbought": ScreenerCriteria(overbought=True)
    }
    
    if preset not in presets:
        return {"error": f"Unknown preset. Available: {list(presets.keys())}"}
    
    return await screen_stocks(presets[preset])
