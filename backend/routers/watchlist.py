"""
Watchlist Router - Watchlist management endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import aiosqlite

from database.db import DATABASE_PATH
from services.market_data import market_service

router = APIRouter()


class WatchlistCreate(BaseModel):
    name: str


class WatchlistItemAdd(BaseModel):
    symbol: str


@router.get("/")
async def get_watchlists():
    """Get all watchlists"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM watchlists")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


@router.post("/")
async def create_watchlist(watchlist: WatchlistCreate):
    """Create a new watchlist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            cursor = await db.execute(
                "INSERT INTO watchlists (name) VALUES (?)",
                (watchlist.name,)
            )
            await db.commit()
            return {"id": cursor.lastrowid, "name": watchlist.name}
        except aiosqlite.IntegrityError:
            raise HTTPException(status_code=400, detail="Watchlist already exists")


@router.get("/{watchlist_id}")
async def get_watchlist(watchlist_id: int):
    """Get watchlist with current quotes"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get watchlist
        cursor = await db.execute(
            "SELECT * FROM watchlists WHERE id = ?",
            (watchlist_id,)
        )
        watchlist = await cursor.fetchone()
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        # Get items
        cursor = await db.execute(
            "SELECT * FROM watchlist_items WHERE watchlist_id = ?",
            (watchlist_id,)
        )
        items = await cursor.fetchall()
        
        # Get quotes for all items
        quotes = []
        for item in items:
            quote = await market_service.get_quote(item["symbol"])
            quotes.append({
                "id": item["id"],
                "symbol": item["symbol"],
                "addedAt": item["added_at"],
                **quote
            })
        
        return {
            "id": dict(watchlist)["id"],
            "name": dict(watchlist)["name"],
            "items": quotes
        }


@router.post("/{watchlist_id}/items")
async def add_to_watchlist(watchlist_id: int, item: WatchlistItemAdd):
    """Add symbol to watchlist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Verify watchlist exists
        cursor = await db.execute(
            "SELECT id FROM watchlists WHERE id = ?",
            (watchlist_id,)
        )
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        try:
            cursor = await db.execute(
                "INSERT INTO watchlist_items (watchlist_id, symbol) VALUES (?, ?)",
                (watchlist_id, item.symbol.upper())
            )
            await db.commit()
            return {"id": cursor.lastrowid, "symbol": item.symbol.upper()}
        except aiosqlite.IntegrityError:
            raise HTTPException(status_code=400, detail="Symbol already in watchlist")


@router.delete("/{watchlist_id}/items/{symbol}")
async def remove_from_watchlist(watchlist_id: int, symbol: str):
    """Remove symbol from watchlist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM watchlist_items WHERE watchlist_id = ? AND symbol = ?",
            (watchlist_id, symbol.upper())
        )
        await db.commit()
        return {"message": f"Removed {symbol.upper()} from watchlist"}


@router.delete("/{watchlist_id}")
async def delete_watchlist(watchlist_id: int):
    """Delete a watchlist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM watchlists WHERE id = ?", (watchlist_id,))
        await db.commit()
        return {"message": "Watchlist deleted"}
