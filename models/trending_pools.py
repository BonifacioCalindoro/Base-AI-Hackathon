from pydantic import BaseModel
from typing import Literal, Dict, List

class GetTrendingPoolsArgs(BaseModel):
    timeframe: Literal['5m', '1h', '6h', '24h']
    page: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] = 1

class PoolAttributes(BaseModel):
    name: str
    address: str
    base_token_price_usd: str
    quote_token_price_usd: str
    base_token_price_native_currency: str
    quote_token_price_native_currency: str
    base_token_price_quote_token: str
    quote_token_price_base_token: str
    pool_created_at: str
    reserve_in_usd: str|None
    fdv_usd: str|None
    market_cap_usd: str|None
    price_change_percentage: Dict
    transactions: Dict
    volume_usd: Dict

class PoolData(BaseModel):
    id: str
    type: str
    attributes: PoolAttributes
    relationships: Dict

class TrendingPoolsResponse(BaseModel):
    data: List[PoolData]