"""
Bloomberg Terminal Alternative - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from routers import market, news, analysis, portfolio, watchlist, screener
from database.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    await init_db()
    print("[*] Bloomberg Terminal Alternative started!")
    yield
    # Shutdown
    print("[*] Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Bloomberg Terminal Alternative",
    description="A comprehensive financial terminal with AI-powered analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market.router, prefix="/api/market", tags=["Market Data"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["AI Analysis"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(screener.router, prefix="/api/screener", tags=["Screener"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Bloomberg Terminal Alternative",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
