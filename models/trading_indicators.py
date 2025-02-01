from pydantic import BaseModel
from typing import Literal

class RSIResponse(BaseModel):
    rsi: float

class CalculateRSIArgs(BaseModel):
    pool_address: str
    timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d']
    period: int = 14

class MACDResponse(BaseModel):
    macd_line: float
    signal_line: float
    histogram: float

class CalculateMACDArgs(BaseModel):
    pool_address: str
    timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d']
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9