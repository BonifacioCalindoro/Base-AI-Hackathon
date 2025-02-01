from typing import Literal

base_url = "https://api.geckoterminal.com/api/v2"

def get_ohlcv_url(pool_address: str, timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d']):
    if timeframe == '1m':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/minute"
    elif timeframe == '5m':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/minute?aggregate=5"
    elif timeframe == '15m':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/minute?aggregate=15"
    elif timeframe == '1h':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/hour"
    elif timeframe == '4h':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/hour?aggregate=4"
    elif timeframe == '12h':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/hour?aggregate=12"
    elif timeframe == '1d':
        return f"{base_url}/networks/base/pools/{pool_address}/ohlcv/day"

def get_trending_pools_url(timeframe: Literal['5m', '1h', '6h', '24h'], page: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] = 1):
    return f"{base_url}/networks/base/trending_pools?page={page}&duration={timeframe}"
    
def get_token_price_url(token: str):
    return f"{base_url}/simple/networks/base/token_price/{token}"

def get_pools_url(pool_address: str):
    return f"{base_url}/networks/base/pools/{pool_address}"

def get_token_info_url(token_address: str):
    return f"{base_url}/networks/base/tokens/{token_address}"

def search_pools_with_query(query: str):
    return f"{base_url}/search/pools?query={query}&network=base"
