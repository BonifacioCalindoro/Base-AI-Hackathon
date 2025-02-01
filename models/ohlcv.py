from pydantic import BaseModel, Field
from typing import List, Tuple, Literal

class GetOHLCVArgs(BaseModel):
    pool_address: str
    timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d']

class TokenInfo(BaseModel):
    address: str
    name: str
    symbol: str
    coingecko_coin_id: str

class OHLCVMeta(BaseModel):
    base: TokenInfo
    quote: TokenInfo

class OHLCVAttributes(BaseModel):
    ohlcv_list: List[List[float]] = Field(
        description="List of OHLCV data points. Each point is [timestamp, open, high, low, close, volume]",
        min_items=1,
        max_items=1000,
    )

class OHLCVData(BaseModel):
    id: str
    type: str
    attributes: OHLCVAttributes

class OHLCVResponse(BaseModel):
    data: OHLCVData
    meta: OHLCVMeta