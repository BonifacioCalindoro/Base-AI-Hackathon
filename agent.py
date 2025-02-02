import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools.ohlcv import get_ohlcv_data_tool
from tools.trending_pools import get_trending_pools_tool
from tools.trading_indicators import get_ohlcv_data_and_calculate_rsi_tool, get_ohlcv_data_and_calculate_macd_tool
from tools.trading_strategies import start_rsi_strategy_tool, stop_rsi_strategy_tool
# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
import json
from tools.pool_search import search_pools_tool

import logfire

load_dotenv()

logfire.configure(
    token=os.getenv('LOGFIRE_TOKEN'),
    service_name='ai_agent',
    send_to_logfire='if-token-present',
    scrubbing=False
)

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet.json"


def initialize_agent():
    with logfire.span(
        f"Initializing agent",
        _tags=['agent_initialize']
    ):
        """Initialize the agent with CDP Agentkit."""
        # Initialize LLM.
        llm = ChatOpenAI(model="gpt-4o-mini")
        logfire.info(
            f"LLM initialized",
            model="gpt-4o-mini",
            _tags=['agent_initialize_llm'])

        wallet_data = None

        if os.path.exists(wallet_data_file):
            with open(wallet_data_file) as f:
                wallet_data = f.read()

            logfire.info(
                f"Wallet data loaded",
                wallet_data=wallet_data,
                _tags=['agent_initialize_wallet_data'])
        else:
            logfire.info(
                f"Wallet data not found",
                _tags=['agent_initialize_wallet_data_not_found'])

        # Configure CDP Agentkit Langchain Extension.
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('CDP_API_KEY_PRIVATE_KEY='):
                    raw_key = line[len('CDP_API_KEY_PRIVATE_KEY='):].strip()
                    break
        
        values = {
            "cdp_api_key_name": os.getenv("CDP_API_KEY_NAME"),
            "cdp_api_key_private_key": raw_key.replace('\\n', '\n'),
        }
        
        if wallet_data is not None:
            # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
            values["cdp_wallet_data"] = wallet_data

        agentkit = CdpAgentkitWrapper(**values)
        logfire.info(
            f"Agentkit initialized",
            agentkit=agentkit,
            _tags=['agent_initialize_agentkit'])

        # persist the agent's CDP MPC Wallet Data.
        wallet_data = agentkit.export_wallet()
        with open(wallet_data_file, "w") as f:
            json.dump(json.loads(wallet_data), f)
        logfire.info(
            f"Wallet data persisted",
            wallet_data=wallet_data,
            _tags=['agent_initialize_wallet_data_persisted'])

        # Initialize CDP Agentkit Toolkit and get tools.
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()
        tools.append(get_ohlcv_data_tool(agentkit))
        tools.append(get_trending_pools_tool(agentkit))
        tools.append(get_ohlcv_data_and_calculate_rsi_tool(agentkit))
        tools.append(get_ohlcv_data_and_calculate_macd_tool(agentkit))
        tools.append(search_pools_tool(agentkit))
        tools.append(start_rsi_strategy_tool(agentkit))
        tools.append(stop_rsi_strategy_tool(agentkit))
        for tool in tools:
            print(tool.name)

        logfire.info(
            f"Tools initialized",
            tools=tools,
            _tags=['agent_initialize_tools'])

        # Store buffered conversation history in memory.
        memory = MemorySaver()
        config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

        logfire.info(
            f"Memory saver initialized",
            memory=memory,
            config=config,
            _tags=['agent_initialize_memory_saver'])
        

        # Create ReAct Agent using the LLM and CDP Agentkit tools.
        agent_response = create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=(
                "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
                "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
                "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
                "details and request funds from the user. Before executing your first action, get the wallet details "
                "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
                "again later. If someone asks you to do something you can't do with your currently available tools, "
                "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
                "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
                "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
            ),
        ), config

        logfire.info(
            f"Agent created",
            _tags=['agent_initialize_agent'])
        return agent_response
