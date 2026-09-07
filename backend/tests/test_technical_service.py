"""
Unit tests for Bloomberg Terminal Technical Analysis Service
"""
import pytest
import pandas as pd
import numpy as np
from services.technical import technical_service


def create_synthetic_df(days: int = 250, start_price: float = 100.0) -> pd.DataFrame:
    """Generates predictable OHLCV dataframe for indicator validation"""
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='B')
    
    # Generate upward trending walk
    returns = np.random.normal(0.001, 0.015, days)
    price_series = start_price * np.exp(np.cumsum(returns))
    
    high = price_series * (1 + np.random.uniform(0.002, 0.015, days))
    low = price_series * (1 - np.random.uniform(0.002, 0.015, days))
    open_p = low + (high - low) * np.random.uniform(0.2, 0.8, days)
    volume = np.random.randint(500_000, 5_000_000, days)
    
    df = pd.DataFrame({
        'Open': open_p,
        'High': high,
        'Low': low,
        'Close': price_series,
        'Volume': volume
    }, index=dates)
    return df


def test_empty_or_small_df():
    """Ensures graceful handling of insufficient data"""
    empty_df = pd.DataFrame()
    res = technical_service.calculate_indicators_from_df(empty_df, "AAPL")
    assert "error" in res

    small_df = create_synthetic_df(days=3)
    res_small = technical_service.calculate_indicators_from_df(small_df, "AAPL")
    assert "error" in res_small


def test_moving_averages_calculation():
    """Validates SMA and EMA calculations"""
    df = create_synthetic_df(days=220)
    result = technical_service.calculate_indicators_from_df(df, "AAPL")
    
    assert "indicators" in result
    mas = result["indicators"]["movingAverages"]
    
    assert mas["sma20"] is not None
    assert mas["sma50"] is not None
    assert mas["sma200"] is not None
    assert mas["ema12"] is not None
    assert mas["ema26"] is not None
    
    # Hand-calculate expected SMA20
    expected_sma20 = round(float(df['Close'].iloc[-20:].mean()), 2)
    assert mas["sma20"] == expected_sma20


def test_rsi_bounds_and_math():
    """Ensures RSI stays bounded within [0, 100]"""
    df = create_synthetic_df(days=60)
    result = technical_service.calculate_indicators_from_df(df, "AAPL")
    
    rsi = result["indicators"]["momentum"]["rsi"]
    assert 0.0 <= rsi <= 100.0


def test_macd_formula_correctness():
    """Verifies Gerald Appel MACD: Histogram = Line - SignalLine"""
    df = create_synthetic_df(days=100)
    result = technical_service.calculate_indicators_from_df(df, "AAPL")
    
    momentum = result["indicators"]["momentum"]
    macd = momentum["macd"]
    signal = momentum["macdSignal"]
    hist = momentum["macdHistogram"]
    
    expected_hist = round(macd - signal, 2)
    assert abs(hist - expected_hist) <= 0.02


def test_bollinger_bands_ordering():
    """Verifies Upper Band >= Middle (SMA20) >= Lower Band"""
    df = create_synthetic_df(days=60)
    result = technical_service.calculate_indicators_from_df(df, "AAPL")
    
    vol = result["indicators"]["volatility"]
    upper = vol["bollingerUpper"]
    middle = vol["bollingerMiddle"]
    lower = vol["bollingerLower"]
    
    assert upper >= middle
    assert middle >= lower


def test_signals_generation():
    """Validates structured trading signal outputs"""
    df = create_synthetic_df(days=220)
    result = technical_service.calculate_indicators_from_df(df, "AAPL")
    
    assert "signals" in result
    assert isinstance(result["signals"], list)
    assert len(result["signals"]) > 0
    for s in result["signals"]:
        assert "type" in s
        assert "signal" in s
        assert "description" in s
