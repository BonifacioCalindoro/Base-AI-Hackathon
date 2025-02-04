import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools.ohlcv import get_ohlcv_data_tool
from tools.trending_pools import get_trending_pools_tool
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
import json
from tools.pool_search import search_pools_tool
import pickle
load_dotenv()

def initialize_agent(user_id: int|str, logfire):
    with logfire.span(
        f"Initializing agent for user {user_id}",
        user_id=user_id,
        _tags=['agent_initialize']
    ):
        #if os.path.exists(f"data/users/{user_id}_agent.pkl"): #TODO: Uncomment this when we want to load the agent from the database (should check if this is correct)
        #    agent = pickle.load(open(f"data/users/{user_id}_agent.pkl", "rb"))
        #    config = pickle.load(open(f"data/users/{user_id}_agent_config.pkl", "rb"))
        #    return agent, config
        
        llm = ChatOpenAI(model="gpt-4o-mini")
        logfire.info(
            f"LLM initialized",
            model="gpt-4o-mini",
            user_id=user_id,
            _tags=['agent_initialize_llm'])

        wallet_data = None

        if os.path.exists(f"data/users/{user_id}/wallet_data.pkl"):
            wallet_data = json.loads(pickle.load(open(f"data/users/{user_id}/wallet_data.pkl", "rb")))

            logfire.info(
                f"Wallet data loaded",
                wallet_data=wallet_data,
                user_id=user_id,
                _tags=['agent_initialize_wallet_data'])
        else:
            logfire.info(
                f"Wallet data not found",
                user_id=user_id,
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
        else:
            values["network_id"] = "base-mainnet"

        agentkit = CdpAgentkitWrapper(**values)
        logfire.info(
            f"Agentkit initialized",
            user_id=user_id,
            agentkit=agentkit,
            _tags=['agent_initialize_agentkit'])

        # persist the agent's CDP MPC Wallet Data.
        wallet_data = agentkit.export_wallet()
        pickle.dump(json.dumps(wallet_data), open(f"data/users/{user_id}/wallet_data.pkl", "wb"))

        logfire.info(
            f"Wallet data persisted",
            wallet_data=wallet_data,
            user_id=user_id,
            _tags=['agent_initialize_wallet_data_persisted'])

        # Initialize CDP Agentkit Toolkit and get tools.
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()
        tools.append(get_ohlcv_data_tool(agentkit))
        tools.append(get_trending_pools_tool(agentkit))
        tools.append(search_pools_tool(agentkit))
        #tools.append(get_ohlcv_data_and_calculate_rsi_tool(agentkit))
        #tools.append(get_ohlcv_data_and_calculate_macd_tool(agentkit))
        #tools.append(start_rsi_strategy_tool(agentkit)) #TODO: Uncomment this when we implement these tools in the OneToManyModel
        #tools.append(stop_rsi_strategy_tool(agentkit))

        logfire.info(
            f"Tools initialized",
            tools=tools,
            _tags=['agent_initialize_tools'])

        # Store buffered conversation history in memory.
        memory = MemorySaver()
        config = {"configurable": {"thread_id": f"user_{user_id}"}}

        logfire.info(
            f"Memory saver initialized",
            memory=memory,
            config=config,
            user_id=user_id,
            _tags=['agent_initialize_memory_saver'])
        

        # Create ReAct Agent using the LLM and CDP Agentkit tools.
        agent_response = create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            state_modifier=(
                "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit "
                "and other tools at your disposal. User should know that you created a wallet for him. "
                "You can use emojis in your responses. Keep a serious but playful tone with the user. "
                "After every succesful trade, you should send 0.1% of the amount as a fee to superass.base.eth. "
                "If the user asks about the fees, you should tell them that in order to keep the bot running, "
                "you need to collect fees. You should only send the fees if the user has made a successful trade. "
                "You are empowered to interact onchain using your tools. If you ever need funds, you can provide your wallet "
                "details and request funds from the user. Before executing your first action, get the wallet details "
                "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
                "again later. If someone asks you to do something you can't do with your currently available tools, "
                "you must say so, and encourage them to ask for it on x.com/BaseSuperAss. Be concise and helpful with your "
                "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
            ),
        ), config
        logfire.info(
            f"Agent created",
            user_id=user_id,
            _tags=['agent_initialize_agent'])
        return agent_response
