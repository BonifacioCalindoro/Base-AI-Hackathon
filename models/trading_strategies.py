from pydantic import BaseModel
from typing import Literal

class StartRSIArgs(BaseModel):
    pool_address: str
    contract_address: str
    timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d']
    period: int = 14
    amount_for_each_buy: float
    strategy_type: Literal['aggressive', 'medium', 'conservative', 'custom']
    price_range_low: float|None
    price_range_high: float|None
    rsi_for_custom_strategy_buy: int|None = None
    rsi_for_custom_strategy_sell: int|None = None

class StartRSIResponse(BaseModel):
    strategy_id: str|None
    success: bool

class StopRSIArgs(BaseModel):
    strategy_id: str|None

class StopRSIResponse(BaseModel):
    success: bool

class GetRSIStatusArgs(BaseModel):
    strategy_id: str|None

class GetRSIStatusResponse(BaseModel):
    status: Literal['running', 'stopped']