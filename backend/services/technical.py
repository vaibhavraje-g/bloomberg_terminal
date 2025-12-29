"""
Technical Analysis Service - Calculate technical indicators
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import yfinance as yf


class TechnicalService:
    """Service for technical analysis calculations"""
    
    async def get_technical_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Calculate common technical indicators for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {"symbol": symbol, "error": "No data available"}
            
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            # Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            sma_200 = close.rolling(window=200).mean().iloc[-1]
            ema_12 = close.ewm(span=12).mean().iloc[-1]
            ema_26 = close.ewm(span=26).mean().iloc[-1]
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD
            macd_line = ema_12 - ema_26
            signal_line = close.ewm(span=9).mean().iloc[-1]
            macd_histogram = macd_line - signal_line
            
            # Bollinger Bands
            std_20 = close.rolling(window=20).std().iloc[-1]
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)
            
            # ATR (Average True Range)
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            # Volume Analysis
            avg_volume_20 = volume.rolling(window=20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / avg_volume_20 if avg_volume_20 > 0 else 1
            
            # Support and Resistance (simplified)
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            
            current_price = close.iloc[-1]
            
            # Trading signals
            signals = []
            
            # Trend signals
            if current_price > sma_50 and sma_50 > sma_200:
                signals.append({"type": "trend", "signal": "bullish", "description": "Price above SMA50 above SMA200"})
            elif current_price < sma_50 and sma_50 < sma_200:
                signals.append({"type": "trend", "signal": "bearish", "description": "Price below SMA50 below SMA200"})
            
            # RSI signals
            if rsi < 30:
                signals.append({"type": "momentum", "signal": "oversold", "description": f"RSI at {rsi:.1f}"})
            elif rsi > 70:
                signals.append({"type": "momentum", "signal": "overbought", "description": f"RSI at {rsi:.1f}"})
            
            # MACD signals
            if macd_histogram > 0:
                signals.append({"type": "macd", "signal": "bullish", "description": "MACD above signal line"})
            else:
                signals.append({"type": "macd", "signal": "bearish", "description": "MACD below signal line"})
            
            return {
                "symbol": symbol.upper(),
                "currentPrice": round(current_price, 2),
                "indicators": {
                    "movingAverages": {
                        "sma20": round(sma_20, 2),
                        "sma50": round(sma_50, 2),
                        "sma200": round(sma_200, 2) if not pd.isna(sma_200) else None,
                        "ema12": round(ema_12, 2),
                        "ema26": round(ema_26, 2)
                    },
                    "momentum": {
                        "rsi": round(rsi, 2),
                        "macd": round(macd_line, 2),
                        "macdSignal": round(signal_line, 2),
                        "macdHistogram": round(macd_histogram, 2)
                    },
                    "volatility": {
                        "atr": round(atr, 2),
                        "bollingerUpper": round(bb_upper, 2),
                        "bollingerMiddle": round(sma_20, 2),
                        "bollingerLower": round(bb_lower, 2)
                    },
                    "volume": {
                        "current": int(volume.iloc[-1]),
                        "average20d": int(avg_volume_20),
                        "ratio": round(volume_ratio, 2)
                    },
                    "levels": {
                        "resistance": round(recent_high, 2),
                        "support": round(recent_low, 2)
                    }
                },
                "signals": signals,
                "trend": "bullish" if current_price > sma_50 else "bearish"
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
    
    async def get_chart_indicators(
        self, 
        symbol: str, 
        period: str = "6mo",
        indicators: List[str] = ["sma20", "sma50", "volume"]
    ) -> Dict[str, Any]:
        """Get indicator data for charting"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {"symbol": symbol, "error": "No data available"}
            
            result = {
                "symbol": symbol.upper(),
                "candles": [],
                "indicators": {}
            }
            
            # Prepare candlestick data
            for index, row in df.iterrows():
                result["candles"].append({
                    "time": int(index.timestamp()),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2)
                })
            
            close = df['Close']
            
            # Calculate requested indicators
            if "sma20" in indicators:
                sma20 = close.rolling(window=20).mean()
                result["indicators"]["sma20"] = [
                    {"time": int(idx.timestamp()), "value": round(val, 2)}
                    for idx, val in sma20.items() if not pd.isna(val)
                ]
            
            if "sma50" in indicators:
                sma50 = close.rolling(window=50).mean()
                result["indicators"]["sma50"] = [
                    {"time": int(idx.timestamp()), "value": round(val, 2)}
                    for idx, val in sma50.items() if not pd.isna(val)
                ]
            
            if "sma200" in indicators:
                sma200 = close.rolling(window=200).mean()
                result["indicators"]["sma200"] = [
                    {"time": int(idx.timestamp()), "value": round(val, 2)}
                    for idx, val in sma200.items() if not pd.isna(val)
                ]
            
            if "volume" in indicators:
                result["indicators"]["volume"] = [
                    {
                        "time": int(idx.timestamp()),
                        "value": int(row["Volume"]),
                        "color": "#26a69a" if row["Close"] >= row["Open"] else "#ef5350"
                    }
                    for idx, row in df.iterrows()
                ]
            
            return result
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}


# Singleton instance
technical_service = TechnicalService()
