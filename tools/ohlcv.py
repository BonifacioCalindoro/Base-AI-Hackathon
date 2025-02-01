from cdp_langchain.tools import CdpTool
from cdp_agentkit_core.actions.cdp_action import CdpAction
import utils.geckoterminal_urls as geckoterminal_urls
from typing import Literal
import requests
from models.ohlcv import OHLCVResponse, GetOHLCVArgs

def get_ohlcv_data(pool_address: str, timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d']) -> OHLCVResponse:
    url = geckoterminal_urls.get_ohlcv_url(pool_address, timeframe)
    response = requests.get(url)
    return OHLCVResponse(**response.json())

OHLCVAction = CdpAction(
    name="get_ohlcv_data",
    description="Get OHLCV candlestick data for a pool",
    args_schema=GetOHLCVArgs,
    func=get_ohlcv_data,
)

def get_ohlcv_data_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=OHLCVAction.name,
        description=OHLCVAction.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=OHLCVAction.args_schema,
        func=OHLCVAction.func,
    )
