"""
News Router - Financial news endpoints
"""
from fastapi import APIRouter, Query
from typing import Optional

from services.news_service import news_service
from services.llm_service import llm_service

router = APIRouter()


@router.get("/")
async def get_news(
    symbol: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50)
):
    """Get financial news"""
    return await news_service.get_news(symbol, limit)


@router.get("/symbol/{symbol}")
async def get_symbol_news(symbol: str, limit: int = Query(20, ge=1, le=50)):
    """Get news for a specific symbol"""
    return await news_service.get_news(symbol, limit)


@router.get("/summary")
async def get_news_summary(symbol: Optional[str] = None):
    """Get AI-generated news summary"""
    news_items = await news_service.get_news(symbol, 10)
    summary = await llm_service.summarize_news(news_items)
    return {
        "summary": summary,
        "newsCount": len(news_items)
    }
