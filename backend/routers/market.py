"""
Market Data Router - Stock quotes, charts, and company information
"""
from fastapi import APIRouter, Query
from typing import List, Optional

from services.market_data import market_service
from services.technical import technical_service

router = APIRouter()


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get real-time quote for a symbol"""
    return await market_service.get_quote(symbol)


@router.get("/quotes")
async def get_quotes(symbols: str = Query(..., description="Comma-separated symbols")):
    """Get quotes for multiple symbols"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    quotes = []
    for symbol in symbol_list:
        quote = await market_service.get_quote(symbol)
        quotes.append(quote)
    return quotes


@router.get("/history/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """Get historical OHLCV data"""
    return await market_service.get_historical_data(symbol, period, interval)


@router.get("/company/{symbol}")
async def get_company_info(symbol: str):
    """Get detailed company information"""
    return await market_service.get_company_info(symbol)


@router.get("/financials/{symbol}")
async def get_financials(symbol: str):
    """Get financial statements"""
    return await market_service.get_financials(symbol)


@router.get("/indices")
async def get_market_indices():
    """Get major market indices"""
    return await market_service.get_market_indices()


@router.get("/sectors")
async def get_sector_performance():
    """Get sector performance"""
    return await market_service.get_sector_performance()


@router.get("/search")
async def search_symbols(q: str = Query(..., min_length=1)):
    """Search for symbols"""
    return await market_service.search_symbols(q)


@router.get("/technical/{symbol}")
async def get_technical_indicators(symbol: str, period: str = "1y"):
    """Get technical indicators for a symbol"""
    return await technical_service.get_technical_indicators(symbol, period)


@router.get("/chart/{symbol}")
async def get_chart_data(
    symbol: str,
    period: str = "6mo",
    indicators: str = Query("sma20,sma50,volume", description="Comma-separated indicators")
):
    """Get chart data with indicators"""
    indicator_list = [i.strip() for i in indicators.split(",")]
    return await technical_service.get_chart_indicators(symbol, period, indicator_list)
