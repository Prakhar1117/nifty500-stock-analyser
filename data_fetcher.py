import yfinance as yf
import pandas as pd
import ta

def fetch_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    Period can be 1mo, 3mo, 6mo, 1y, 2y, 5y, max, etc.
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add SMA, EMA, RSI, and MACD to the dataframe.
    """
    if df.empty or len(df) < 30: # Need enough data points for indicators
        return df
        
    # Clean NaN values
    df_clean = df.copy()

    try:
        # Simple Moving Averages
        df_clean['SMA_20'] = ta.trend.sma_indicator(df_clean['Close'], window=20)
        df_clean['SMA_50'] = ta.trend.sma_indicator(df_clean['Close'], window=50)

        # Exponential Moving Average
        df_clean['EMA_20'] = ta.trend.ema_indicator(df_clean['Close'], window=20)

        # RSI
        df_clean['RSI'] = ta.momentum.rsi(df_clean['Close'], window=14)

        # MACD
        macd = ta.trend.MACD(df_clean['Close'])
        df_clean['MACD'] = macd.macd()
        df_clean['MACD_Signal'] = macd.macd_signal()
        df_clean['MACD_Diff'] = macd.macd_diff()
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        
    return df_clean
