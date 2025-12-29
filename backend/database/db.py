"""
Database initialization and management
"""
import aiosqlite
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "terminal.db"


async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Watchlist table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Watchlist items table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS watchlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
                UNIQUE(watchlist_id, symbol)
            )
        """)
        
        # Portfolio table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Portfolio holdings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_cost REAL NOT NULL,
                purchase_date DATE,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
            )
        """)
        
        # Create default watchlist if none exists
        await db.execute("""
            INSERT OR IGNORE INTO watchlists (name) VALUES ('Default')
        """)
        
        # Create default portfolio if none exists
        await db.execute("""
            INSERT OR IGNORE INTO portfolios (name) VALUES ('My Portfolio')
        """)
        
        await db.commit()
        print("[+] Database initialized")


async def get_db():
    """Get database connection"""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
