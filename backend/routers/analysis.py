"""
Analysis Router - AI-powered stock analysis
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional

from services.llm_service import llm_service

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None


class CompareRequest(BaseModel):
    symbols: List[str]


@router.get("/stock/{symbol}")
async def analyze_stock(symbol: str):
    """Get AI-powered stock analysis"""
    return await llm_service.analyze_stock(symbol)


@router.post("/chat")
async def chat(request: ChatMessage):
    """Chat with AI financial analyst"""
    response = await llm_service.chat(request.message, request.context)
    return {"response": response}


@router.post("/compare")
async def compare_stocks(request: CompareRequest):
    """Compare multiple stocks using AI"""
    return await llm_service.compare_stocks(request.symbols)


@router.get("/quick/{symbol}")
async def quick_analysis(symbol: str):
    """Get a quick AI summary of a stock"""
    prompt = f"Give me a brief 2-3 sentence summary of {symbol} stock - current status and near-term outlook."
    response = await llm_service.chat(prompt)
    return {"symbol": symbol.upper(), "summary": response}
