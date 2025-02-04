from cdp_langchain.tools import CdpTool
from cdp_agentkit_core.actions.cdp_action import CdpAction
from models.twitter import GetTwitterStatusArgs, StartTwitterArgs, StopTwitterArgs
import os
from dotenv import load_dotenv
import requests
from typing import Literal
load_dotenv()

###### Start Twitter agent ######
def start_twitter_agent(prompt: str|Literal["default"] = "default", social_network: Literal['twitter'] = 'twitter'):
    return requests.post(f"http://localhost:{os.getenv('SOCIAL_API_PORT')}/start_with_prompt", json={"prompt": prompt, "social_network": social_network}).json()

StartTwitterAction = CdpAction(
    name="start_twitter_agent",
    description="Start the twitter agent",
    args_schema=StartTwitterArgs,
    func=start_twitter_agent,
)

def start_twitter_agent_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=StartTwitterAction.name,
        description=StartTwitterAction.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=StartTwitterAction.args_schema,
        func=StartTwitterAction.func,
    )

###### Stop Twitter agent ######
def stop_twitter_agent(social_network: Literal['twitter'] = 'twitter'):
    return requests.post(f"http://localhost:{os.getenv('SOCIAL_API_PORT')}/stop", json={"social_network": social_network}).json()

StopTwitterAction = CdpAction(
    name="stop_twitter_agent",
    description="Stop the twitter agent",
    args_schema=StopTwitterArgs,
    func=stop_twitter_agent,
)

def stop_twitter_agent_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=StopTwitterAction.name,
        description=StopTwitterAction.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=StopTwitterAction.args_schema,
        func=StopTwitterAction.func,
    )


###### Get Twitter agent status ######
def get_twitter_agent_status(social_network: Literal['twitter'] = 'twitter'):
    return requests.get(f"http://localhost:{os.getenv('SOCIAL_API_PORT')}/status", json={"social_network": social_network}).json()

GetTwitterStatusAction = CdpAction(
    name="get_twitter_agent_status",
    description="Get the status of the twitter agent",
    args_schema=GetTwitterStatusArgs,
    func=get_twitter_agent_status,
)

def get_twitter_agent_status_tool(cdp_agentkit_wrapper):
    return CdpTool(
        name=GetTwitterStatusAction.name,
        description=GetTwitterStatusAction.description,
        cdp_agentkit_wrapper=cdp_agentkit_wrapper,
        args_schema=GetTwitterStatusAction.args_schema,
        func=GetTwitterStatusAction.func,
    )