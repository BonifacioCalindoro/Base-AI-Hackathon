from cdp_langchain.tools import CdpTool
from cdp_agentkit_core.actions.cdp_action import CdpAction
from typing import Literal
from models.ohlcv import OHLCVResponse, GetOHLCVArgs
from tools.ohlcv import get_ohlcv_data
from models.trading_indicators import CalculateRSIArgs, RSIResponse, MACDResponse, CalculateMACDArgs

def get_ohlcv_data_and_calculate_rsi(pool_address: str, timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d'], period: int = 14) -> RSIResponse:
    """
    Get OHLCV data and calculate the Relative Strength Index (RSI).
    
    Args:
        pool_address: The address of the pool to get OHLCV data for
        timeframe: The timeframe to get OHLCV data for
        period: The period over which to calculate RSI (default 14)
        
    Returns:
        The RSI value for the most recent period
    """
    ohlcv_data = get_ohlcv_data(pool_address, timeframe)

    # Reverse the OHLCV list to have most recent data first
    ohlcv_data.data.attributes.ohlcv_list.reverse()

    if len(ohlcv_data.data.attributes.ohlcv_list) < period + 1:
        raise ValueError(f"Not enough data points. Need at least {period + 1} data points.")

    # Get closing prices
    closes = [float(candle[4]) for candle in ohlcv_data.data.attributes.ohlcv_list]
    
    # Calculate price changes
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    
    # Separate gains and losses
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    # Calculate average gains and losses
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Calculate subsequent values
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    # Calculate RS and RSI
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return RSIResponse(rsi=rsi)

RSI_Action = CdpAction(
    name="get_ohlcv_data_and_calculate_rsi",
    description="Get OHLCV data and calculate the Relative Strength Index (RSI) for a given OHLCV dataset",
    args_schema=CalculateRSIArgs,
    func=get_ohlcv_data_and_calculate_rsi,
)

def get_ohlcv_data_and_calculate_rsi_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=RSI_Action.name,
        description=RSI_Action.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=RSI_Action.args_schema,
        func=RSI_Action.func,
    )

def calculate_ema(prices: list, period: int) -> float:
    """Calculate Exponential Moving Average"""
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema

def get_ohlcv_data_and_calculate_macd(
    pool_address: str, 
    timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d'],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> MACDResponse:
    """
    Get OHLCV data and calculate the Moving Average Convergence Divergence (MACD).
    
    Args:
        pool_address: The address of the pool to get OHLCV data for
        timeframe: The timeframe to get OHLCV data for
        fast_period: The period for the fast EMA (default 12)
        slow_period: The period for the slow EMA (default 26)
        signal_period: The period for the signal line EMA (default 9)
        
    Returns:
        MACDResponse containing the MACD line, signal line, and histogram values
    """
    ohlcv_data = get_ohlcv_data(pool_address, timeframe)
    
    # Reverse the OHLCV list to have most recent data first
    ohlcv_data.data.attributes.ohlcv_list.reverse()
    
    required_points = max(fast_period, slow_period) + signal_period
    if len(ohlcv_data.data.attributes.ohlcv_list) < required_points:
        raise ValueError(f"Not enough data points. Need at least {required_points} data points.")

    # Get closing prices
    closes = [float(candle[4]) for candle in ohlcv_data.data.attributes.ohlcv_list]
    
    # Calculate fast and slow EMAs
    fast_ema = calculate_ema(closes[:fast_period], fast_period)
    slow_ema = calculate_ema(closes[:slow_period], slow_period)
    
    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    
    # Calculate signal line (9-day EMA of MACD line)
    macd_values = [macd_line]  # Store historical MACD values
    signal_line = calculate_ema(macd_values[:signal_period], signal_period)
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return MACDResponse(
        macd_line=macd_line,
        signal_line=signal_line,
        histogram=histogram
    )

MACD_Action = CdpAction(
    name="get_ohlcv_data_and_calculate_macd",
    description="Get OHLCV data and calculate the Moving Average Convergence Divergence (MACD) indicator",
    args_schema=CalculateMACDArgs,
    func=get_ohlcv_data_and_calculate_macd,
)

def get_ohlcv_data_and_calculate_macd_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=MACD_Action.name,
        description=MACD_Action.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=MACD_Action.args_schema,
        func=MACD_Action.func,
    )