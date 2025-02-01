from cdp_langchain.tools import CdpTool
from cdp_agentkit_core.actions.cdp_action import CdpAction
import utils.geckoterminal_urls as geckoterminal_urls
from typing import Literal
import requests
from models.trending_pools import TrendingPoolsResponse, GetTrendingPoolsArgs

def get_trending_pools(timeframe: Literal['5m', '1h', '6h', '24h'], page: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] = 1) -> TrendingPoolsResponse:
    url = geckoterminal_urls.get_trending_pools_url(timeframe, page)
    response = requests.get(url)
    return response.json()

TrendingPoolsAction = CdpAction(
    name="get_trending_pools",
    description="Get trending pools",
    args_schema=GetTrendingPoolsArgs,
    func=get_trending_pools,
)

def get_trending_pools_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=TrendingPoolsAction.name,
        description=TrendingPoolsAction.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=TrendingPoolsAction.args_schema,
        func=TrendingPoolsAction.func,
    )