from fastapi import FastAPI, BackgroundTasks
import uvicorn
import logfire
from typing import Literal
import os
import asyncio
from social.twitter.agent import initialize_agent as initialize_twitter_agent
from social.twitter.agent import check_mentions as check_twitter_mentions, post as post_to_twitter
from dotenv import load_dotenv
import time

load_dotenv()

app = FastAPI()

logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    service_name="social_API",
    send_to_logfire="if-token-present",
    scrubbing=False
)

running_loop = False
running_social = {
    "twitter": False,
    #"farcaster": False #TODO: implement farcaster
}

global_prompt = 'Post on twitter about how cool SuperAssistant is!'
last_time_checked_twitter_mentions = 0
last_time_posted_on_twitter = 0
mentions_rate_limit = 60*60*8
post_rate_limit = 60*60*1.5
twitter_agent, config = initialize_twitter_agent()
responses = {
    "twitter": {
        "check_mentions": [],
        "post": []
    }
}

async def main_loop():
    global global_prompt
    global running_social
    global running_loop
    global last_time_checked_twitter_mentions
    global last_time_posted_on_twitter
    global responses
    while True:
        if not running_loop:
            break
        if running_social["twitter"]:
            if time.time() > last_time_checked_twitter_mentions + mentions_rate_limit:
                response = check_twitter_mentions(
                    agent_executor=twitter_agent,
                    config=config
                )
                responses["twitter"]["check_mentions"].append({
                    "agent_response": response,
                    "timestamp": time.time()
                })
                last_time_checked_twitter_mentions = time.time()
        if running_social["twitter"]:
            if time.time() > last_time_posted_on_twitter + post_rate_limit:
                response = post_to_twitter(
                    agent_executor=twitter_agent,
                    config=config,
                    prompt=global_prompt
                )
                responses["twitter"]["post"].append({
                    "agent_response": response,
                    "timestamp": time.time()
                })
                last_time_posted_on_twitter = time.time()
        await asyncio.sleep(10)


@app.post("/start_with_prompt")
async def start_with_prompt(background_tasks: BackgroundTasks, prompt: str|Literal["default"] = "default", social_network: Literal["twitter"] = "twitter"):
    global running_loop
    global global_prompt
    global running_social
    global_prompt = prompt if prompt != "default" else global_prompt
    if not running_loop:
        running_loop = True
        running_social[social_network] = True
        background_tasks.add_task(main_loop)
        return f"Started {social_network} agent with prompt: {prompt}"
    else:
        return f"Already running {social_network} agent, changed prompt to: {prompt}"
    
@app.post("/stop")
async def stop_loop(social_network: Literal["twitter", None] = None): # By default (None) will stop bot socials all loops
    global running_social
    global running_loop
    if not social_network:
        running_loop = False
        running_social = {
            "twitter": False,
        }
    else:
        running_social[social_network] = False
    if not running_social["twitter"]:
        running_loop = False
    return f"Stopped {social_network}" if social_network else "Stopped all"


@app.get("/status")
async def get_status(social_network: Literal["twitter"]):
    return {
        "running": running_loop,
        "running_social": running_social,
        "prompt": global_prompt,
        "last_time_checked_mentions": last_time_checked_twitter_mentions if social_network == "twitter" else None, #already preapred to add more socials
        "last_time_posted": last_time_posted_on_twitter if social_network == "twitter" else None, #already preapred to add more socials
        "agent_responses": responses[social_network]
    }


if __name__ == "__main__":
    logfire.info("Starting social API", _tags=["social_api"])
    try:
        uvicorn.run(app, host='localhost', port=os.getenv("SOCIAL_API_PORT") or 42070)
    except KeyboardInterrupt:
        logfire.info("Social API stopped", _tags=["social_api"])
    except Exception as e:
        logfire.error(f"Error running social API: {e}", _tags=["social_api"])
        raise e
