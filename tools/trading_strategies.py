from cdp_langchain.tools import CdpTool
from cdp_agentkit_core.actions.cdp_action import CdpAction
from typing import Literal
from models.trading_strategies import StartRSIArgs, StartRSIResponse, StopRSIArgs, StopRSIResponse, GetRSIStatusArgs, GetRSIStatusResponse
import requests

def start_rsi_strategy(
    pool_address: str,
    contract_address: str,
    timeframe: Literal['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d'],
    amount_for_each_buy: float,
    period: int = 14,
    price_range_low: float|None = None,
    price_range_high: float|None = None,
    strategy_type: Literal['aggressive', 'medium', 'conservative', 'custom'] = 'medium',
    rsi_for_custom_strategy_buy: int|None = None,
    rsi_for_custom_strategy_sell: int|None = None,
) -> StartRSIResponse:
    """
    Start an RSI strategy for a given token. If the user does not provide all the data, you will need to ask for it.
    
    Args:
        contract_address: The address of the token to start the strategy for
        timeframe: The timeframe to use for the strategy
        amount_for_each_buy: The amount of the token to buy on each buy
        period: The period to use for the RSI calculation (optional, default is 14)
        price_range_low: The low price range to use for the strategy (optional)
        price_range_high: The high price range to use for the strategy (optional)
        strategy_type: The type of strategy to use (optional, default is 'medium')
        rsi_for_custom_strategy_buy: The RSI value to use for the buy strategy (optional)
        rsi_for_custom_strategy_sell: The RSI value to use for the sell strategy (optional)
        
    Returns:
        The ID of the strategy if it was started successfully, otherwise None
    """
    args = StartRSIArgs(
        pool_address=pool_address,
        contract_address=contract_address,
        timeframe=timeframe,
        amount_for_each_buy=amount_for_each_buy,
        period=period,
        price_range_low=price_range_low,
        price_range_high=price_range_high,
        strategy_type=strategy_type,
        rsi_for_custom_strategy_buy=rsi_for_custom_strategy_buy,
        rsi_for_custom_strategy_sell=rsi_for_custom_strategy_sell,
    )
    return requests.post(f"http://localhost:42069/start_rsi_strategy", json=args.model_dump(), timeout=30).json()

StartRSI_Action = CdpAction(
    name="start_rsi_strategy",
    description="Start an RSI strategy for a given token. If the user does not provide all the data, you will need to ask for it.",
    args_schema=StartRSIArgs,
    func=start_rsi_strategy,
)

def start_rsi_strategy_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=StartRSI_Action.name,
        description=StartRSI_Action.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=StartRSI_Action.args_schema,
        func=StartRSI_Action.func,
    )

def stop_rsi_strategy(strategy_id: str|None = None) -> StopRSIResponse:
    """
    Stop an RSI strategy for a given strategy ID.

    Args:
        strategy_id: The ID of the strategy to stop
        
    Returns:
        True if the strategy was stopped successfully, otherwise False
    """
    return requests.post(f"http://localhost:42069/stop_rsi_strategy", json=StopRSIArgs(strategy_id=strategy_id).model_dump(), timeout=30).json()

StopRSI_Action = CdpAction(
    name="stop_rsi_strategy",
    description="Stop an RSI strategy for a given strategy ID. If the user does not provide the strategy ID, you should use None to stop all strategies.",
    args_schema=StopRSIArgs,
    func=stop_rsi_strategy,
)

def stop_rsi_strategy_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=StopRSI_Action.name,
        description=StopRSI_Action.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=StopRSI_Action.args_schema,
        func=StopRSI_Action.func,
    )