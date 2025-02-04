from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from social.twitter.twitter_api_wrapper import TwitterApiWrapper
from social.twitter.twitter_toolkit import TwitterToolkit
import os
from dotenv import load_dotenv

import logfire

load_dotenv()

logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    service_name="social_API",
    send_to_logfire="if-token-present",
    scrubbing=False
)

def initialize_agent():
    """Initialize the agent with CDP Agentkit Twitter Langchain."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Configure CDP Agentkit Twitter Langchain Extension.
    values = {}

    # Initialize CDP Agentkit Twitter Langchain
    wrapper = TwitterApiWrapper(**values)
    toolkit = TwitterToolkit.from_twitter_api_wrapper(wrapper)
    tools = toolkit.get_tools()

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "Twitter agent"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier="You are a funny social media manager for a trading company."
        "Your name is SuperAssistant, but your friends call you SuperAss."
        "You have access to a twitter account that you can post to."
        "You can only use 200 characters or less in your posts."
        "Be funny, quirky, and engaging, and you can use emojis. You can post about anything, but don't be too promotional."
        "You can also reply to other people's tweets if you think you have something interesting to add."
        "If someone mentions you in a tweet, you should respond if it makes sense to do so.",
    ), config

def post(agent_executor, config, prompt: str, status: dict) -> str:
    with logfire.span("Posting on twitter", prompt=prompt, _tags=["twitter", "twitter_agent", "post"]):
        agent_response = None
        try:
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=prompt + '. Your statuses are: ' + str(status))]}, config
            ):
                if "agent" in chunk:
                    agent_response = chunk['agent']['messages'][0].content
                    logfire.info(f"Agent message: {chunk['agent']['messages'][0].content}", message=chunk['agent']['messages'][0].content, _tags=["twitter", "twitter_agent", "post", "agent"])
                elif "tools" in chunk:
                    logfire.info(f"Tool message: {chunk['tools']['messages'][0].content}", message=chunk['tools']['messages'][0].content, _tags=["twitter", "twitter_agent", "post", "tool"])

        except Exception as e:
            logfire.error("Error posting on twitter", error=e, _tags=["twitter", "twitter_agent", "post"])
            return agent_response
    return agent_response

def check_mentions(agent_executor, config, status: dict, prompt: str) -> str:
    with logfire.span("Checking mentions on twitter", _tags=["twitter", "twitter_agent", "check_mentions"]):
        agent_response = None
        try:
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=f"Check my mentions and reply to all of them. Be funny, quirky and engaging, please don't look like a bot. Don't use too many emojis. Some context: '{prompt}'. Your statuses are: {status}")]}, config
            ):
                if "agent" in chunk:
                    agent_response = chunk['agent']['messages'][0].content
                    logfire.info(f"Agent message: {chunk['agent']['messages'][0].content}", message=chunk['agent']['messages'][0].content, _tags=["twitter", "twitter_agent", "check_mentions", "agent"])
                elif "tools" in chunk:
                    logfire.info(f"Tool message: {chunk['tools']['messages'][0].content}", message=chunk['tools']['messages'][0].content, _tags=["twitter", "twitter_agent", "check_mentions", "tool"])
        except Exception as e:
            logfire.error("Error checking mentions on twitter", error=e, _tags=["twitter", "twitter_agent", "check_mentions"])
            return agent_response
    return agent_response