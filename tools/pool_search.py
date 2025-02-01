from cdp_langchain.tools import CdpTool
from cdp_agentkit_core.actions.cdp_action import CdpAction
import utils.geckoterminal_urls as geckoterminal_urls
import requests
from models.pool_search import SearchPoolsArgs

def search_pools(query: str):
    """
    Search for pools using a query string.
    
    Args:
        query: The search query string (can be token name, symbol, or address)
        
    Returns:
        List of pools matching the search query
    """
    url = geckoterminal_urls.search_pools_with_query(query)
    response = requests.get(url)
    return response.json()

PoolSearchAction = CdpAction(
    name="search_pools",
    description="Search for pools and token information using a query string (token name, symbol, or address)",
    args_schema=SearchPoolsArgs,
    func=search_pools,
)

def search_pools_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=PoolSearchAction.name,
        description=PoolSearchAction.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=PoolSearchAction.args_schema,
        func=PoolSearchAction.func,
    ) 