"""
Technical Analysis Service - Calculate technical indicators
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import yfinance as yf


class TechnicalService:
    """Service for technical analysis calculations"""

    def calculate_indicators_from_df(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Pure calculation method on historical price DataFrame"""
        if df is None or df.empty or len(df) < 5:
            return {"symbol": symbol.upper(), "error": "Insufficient data points for technical analysis"}

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        # Moving Averages
        sma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else close.mean()
        sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
        sma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None

        ema_12_series = close.ewm(span=12, adjust=False).mean()
        ema_26_series = close.ewm(span=26, adjust=False).mean()
        ema_12 = ema_12_series.iloc[-1]
        ema_26 = ema_26_series.iloc[-1]

        # RSI calculation
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = (-delta.clip(upper=0)).rolling(window=14).mean()
        
        last_gain = gain.iloc[-1] if not pd.isna(gain.iloc[-1]) else 0.0
        last_loss = loss.iloc[-1] if not pd.isna(loss.iloc[-1]) else 0.0
        if last_loss == 0:
            rsi = 100.0 if last_gain > 0 else 50.0
        else:
            rs = last_gain / last_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))

        # True MACD Line & 9-period Signal Line on the MACD series
        macd_series = ema_12_series - ema_26_series
        signal_series = macd_series.ewm(span=9, adjust=False).mean()
        macd_hist_series = macd_series - signal_series

        macd_line = macd_series.iloc[-1]
        signal_line = signal_series.iloc[-1]
        macd_histogram = macd_hist_series.iloc[-1]

        # Bollinger Bands (20-period, 2 std dev)
        window_bb = min(20, len(close))
        std_20 = close.rolling(window=window_bb).std().iloc[-1] if window_bb > 1 else 0.0
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)

        # ATR (Average True Range)
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=min(14, len(tr))).mean().iloc[-1]

        # Volume Analysis
        avg_vol_window = min(20, len(volume))
        avg_volume_20 = volume.rolling(window=avg_vol_window).mean().iloc[-1] if avg_vol_window > 0 else volume.iloc[-1]
        volume_ratio = volume.iloc[-1] / avg_volume_20 if avg_volume_20 > 0 else 1.0

        # Support and Resistance
        recent_high = high.tail(min(20, len(high))).max()
        recent_low = low.tail(min(20, len(low))).min()

        current_price = close.iloc[-1]

        # Trading signals
        signals = []

        # Trend signals
        if sma_50 is not None and sma_200 is not None:
            if current_price > sma_50 and sma_50 > sma_200:
                signals.append({"type": "trend", "signal": "bullish", "description": "Price above SMA50 above SMA200 (Golden alignment)"})
            elif current_price < sma_50 and sma_50 < sma_200:
                signals.append({"type": "trend", "signal": "bearish", "description": "Price below SMA50 below SMA200 (Death cross alignment)"})
        elif sma_50 is not None:
            if current_price > sma_50:
                signals.append({"type": "trend", "signal": "bullish", "description": "Price above SMA50"})
            else:
                signals.append({"type": "trend", "signal": "bearish", "description": "Price below SMA50"})

        # RSI signals
        if rsi < 30:
            signals.append({"type": "momentum", "signal": "oversold", "description": f"RSI at {rsi:.1f} indicates oversold condition"})
        elif rsi > 70:
            signals.append({"type": "momentum", "signal": "overbought", "description": f"RSI at {rsi:.1f} indicates overbought condition"})
        else:
            signals.append({"type": "momentum", "signal": "neutral", "description": f"RSI at {rsi:.1f} in neutral zone"})

        # MACD signals
        if macd_histogram > 0:
            signals.append({"type": "macd", "signal": "bullish", "description": "MACD line above signal line (Positive momentum)"})
        else:
            signals.append({"type": "macd", "signal": "bearish", "description": "MACD line below signal line (Negative momentum)"})

        is_bullish = current_price > sma_50 if sma_50 is not None else current_price > sma_20

        return {
            "symbol": symbol.upper(),
            "currentPrice": round(float(current_price), 2),
            "indicators": {
                "movingAverages": {
                    "sma20": round(float(sma_20), 2) if not pd.isna(sma_20) else None,
                    "sma50": round(float(sma_50), 2) if sma_50 is not None and not pd.isna(sma_50) else None,
                    "sma200": round(float(sma_200), 2) if sma_200 is not None and not pd.isna(sma_200) else None,
                    "ema12": round(float(ema_12), 2),
                    "ema26": round(float(ema_26), 2)
                },
                "momentum": {
                    "rsi": round(float(rsi), 2),
                    "macd": round(float(macd_line), 2),
                    "macdSignal": round(float(signal_line), 2),
                    "macdHistogram": round(float(macd_histogram), 2)
                },
                "volatility": {
                    "atr": round(float(atr), 2) if not pd.isna(atr) else 0.0,
                    "bollingerUpper": round(float(bb_upper), 2),
                    "bollingerMiddle": round(float(sma_20), 2),
                    "bollingerLower": round(float(bb_lower), 2)
                },
                "volume": {
                    "current": int(volume.iloc[-1]),
                    "average20d": int(avg_volume_20),
                    "ratio": round(float(volume_ratio), 2)
                },
                "levels": {
                    "resistance": round(float(recent_high), 2),
                    "support": round(float(recent_low), 2)
                }
            },
            "signals": signals,
            "trend": "bullish" if is_bullish else "bearish"
        }

    async def get_technical_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Calculate common technical indicators for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)

            if df.empty:
                return {"symbol": symbol.upper(), "error": "No data available"}

            return self.calculate_indicators_from_df(df, symbol)
        except Exception as e:
            return {"symbol": symbol.upper(), "error": str(e)}

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
                return {"symbol": symbol.upper(), "error": "No data available"}

            result = {
                "symbol": symbol.upper(),
                "candles": [],
                "indicators": {}
            }

            for index, row in df.iterrows():
                result["candles"].append({
                    "time": int(index.timestamp()),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2)
                })

            close = df['Close']

            if "sma20" in indicators:
                sma20 = close.rolling(window=20).mean()
                result["indicators"]["sma20"] = [
                    {"time": int(idx.timestamp()), "value": round(float(val), 2)}
                    for idx, val in sma20.items() if not pd.isna(val)
                ]

            if "sma50" in indicators:
                sma50 = close.rolling(window=50).mean()
                result["indicators"]["sma50"] = [
                    {"time": int(idx.timestamp()), "value": round(float(val), 2)}
                    for idx, val in sma50.items() if not pd.isna(val)
                ]

            if "sma200" in indicators:
                sma200 = close.rolling(window=200).mean()
                result["indicators"]["sma200"] = [
                    {"time": int(idx.timestamp()), "value": round(float(val), 2)}
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
            return {"symbol": symbol.upper(), "error": str(e)}


technical_service = TechnicalService()
