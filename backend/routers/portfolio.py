"""
Portfolio Router - Portfolio management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import aiosqlite

from database.db import get_db, DATABASE_PATH
from services.market_data import market_service

router = APIRouter()


class PortfolioCreate(BaseModel):
    name: str


class HoldingCreate(BaseModel):
    symbol: str
    quantity: float
    avg_cost: float
    purchase_date: Optional[str] = None


class HoldingUpdate(BaseModel):
    quantity: Optional[float] = None
    avg_cost: Optional[float] = None


@router.get("/")
async def get_portfolios():
    """Get all portfolios"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM portfolios")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


@router.post("/")
async def create_portfolio(portfolio: PortfolioCreate):
    """Create a new portfolio"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            cursor = await db.execute(
                "INSERT INTO portfolios (name) VALUES (?)",
                (portfolio.name,)
            )
            await db.commit()
            return {"id": cursor.lastrowid, "name": portfolio.name}
        except aiosqlite.IntegrityError:
            raise HTTPException(status_code=400, detail="Portfolio already exists")


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    """Get portfolio with holdings and current values"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get portfolio
        cursor = await db.execute(
            "SELECT * FROM portfolios WHERE id = ?",
            (portfolio_id,)
        )
        portfolio = await cursor.fetchone()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get holdings
        cursor = await db.execute(
            "SELECT * FROM holdings WHERE portfolio_id = ?",
            (portfolio_id,)
        )
        holdings_rows = await cursor.fetchall()
        
        holdings = []
        total_value = 0
        total_cost = 0
        
        for row in holdings_rows:
            holding = dict(row)
            # Get current price
            quote = await market_service.get_quote(holding["symbol"])
            current_price = quote.get("price", 0)
            
            market_value = current_price * holding["quantity"]
            cost_basis = holding["avg_cost"] * holding["quantity"]
            gain_loss = market_value - cost_basis
            gain_loss_percent = ((current_price - holding["avg_cost"]) / holding["avg_cost"] * 100) if holding["avg_cost"] > 0 else 0
            
            holdings.append({
                **holding,
                "currentPrice": current_price,
                "marketValue": round(market_value, 2),
                "costBasis": round(cost_basis, 2),
                "gainLoss": round(gain_loss, 2),
                "gainLossPercent": round(gain_loss_percent, 2),
                "change": quote.get("change", 0),
                "changePercent": quote.get("changePercent", 0)
            })
            
            total_value += market_value
            total_cost += cost_basis
        
        return {
            "id": dict(portfolio)["id"],
            "name": dict(portfolio)["name"],
            "holdings": holdings,
            "summary": {
                "totalValue": round(total_value, 2),
                "totalCost": round(total_cost, 2),
                "totalGainLoss": round(total_value - total_cost, 2),
                "totalGainLossPercent": round(((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0, 2),
                "holdingsCount": len(holdings)
            }
        }


@router.post("/{portfolio_id}/holdings")
async def add_holding(portfolio_id: int, holding: HoldingCreate):
    """Add a holding to portfolio"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Verify portfolio exists
        cursor = await db.execute(
            "SELECT id FROM portfolios WHERE id = ?",
            (portfolio_id,)
        )
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Check if holding already exists
        cursor = await db.execute(
            "SELECT id, quantity, avg_cost FROM holdings WHERE portfolio_id = ? AND symbol = ?",
            (portfolio_id, holding.symbol.upper())
        )
        existing = await cursor.fetchone()
        
        if existing:
            # Update existing holding (average cost)
            old_qty = existing[1]
            old_cost = existing[2]
            new_qty = old_qty + holding.quantity
            new_avg_cost = ((old_qty * old_cost) + (holding.quantity * holding.avg_cost)) / new_qty
            
            await db.execute(
                "UPDATE holdings SET quantity = ?, avg_cost = ? WHERE id = ?",
                (new_qty, new_avg_cost, existing[0])
            )
            await db.commit()
            return {"id": existing[0], "symbol": holding.symbol.upper(), "quantity": new_qty, "avg_cost": round(new_avg_cost, 2)}
        else:
            cursor = await db.execute(
                "INSERT INTO holdings (portfolio_id, symbol, quantity, avg_cost, purchase_date) VALUES (?, ?, ?, ?, ?)",
                (portfolio_id, holding.symbol.upper(), holding.quantity, holding.avg_cost, holding.purchase_date)
            )
            await db.commit()
            return {"id": cursor.lastrowid, **holding.model_dump()}


@router.delete("/{portfolio_id}/holdings/{symbol}")
async def remove_holding(portfolio_id: int, symbol: str):
    """Remove a holding from portfolio"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM holdings WHERE portfolio_id = ? AND symbol = ?",
            (portfolio_id, symbol.upper())
        )
        await db.commit()
        return {"message": f"Removed {symbol.upper()} from portfolio"}


@router.put("/{portfolio_id}/holdings/{symbol}")
async def update_holding(portfolio_id: int, symbol: str, update: HoldingUpdate):
    """Update a holding"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        updates = []
        values = []
        
        if update.quantity is not None:
            updates.append("quantity = ?")
            values.append(update.quantity)
        if update.avg_cost is not None:
            updates.append("avg_cost = ?")
            values.append(update.avg_cost)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        values.extend([portfolio_id, symbol.upper()])
        
        await db.execute(
            f"UPDATE holdings SET {', '.join(updates)} WHERE portfolio_id = ? AND symbol = ?",
            values
        )
        await db.commit()
        return {"message": f"Updated {symbol.upper()}"}
