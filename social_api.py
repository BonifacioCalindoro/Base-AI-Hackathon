from fastapi import FastAPI, BackgroundTasks
import uvicorn
import logfire
from typing import Literal
import os
import asyncio
from social.twitter.agent import initialize_agent as initialize_twitter_agent
from social.twitter.agent import check_mentions as check_twitter_mentions, post as post_to_twitter
from models.twitter import StartTwitterArgs, StopTwitterArgs, GetTwitterStatusArgs
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
post_rate_limit = 60*60*3
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
async def start_with_prompt(args: StartTwitterArgs, background_tasks: BackgroundTasks):
    global running_loop
    global global_prompt
    global running_social
    global_prompt = args.prompt if args.prompt != "default" else global_prompt
    if not running_loop:
        running_loop = True
        running_social[args.social_network] = True
        background_tasks.add_task(main_loop)
        return f"Started {args.social_network} agent with prompt: {args.prompt}"
    else:
        return f"Already running {args.social_network} agent, changed prompt to: {args.prompt}"
    
@app.post("/stop")
async def stop_loop(args: StopTwitterArgs):
    global running_social
    global running_loop
    if not args.social_network:
        running_loop = False
        running_social = {
            "twitter": False,
        }
    else:
        running_social[args.social_network] = False
    if not running_social[args.social_network]:
        running_loop = False
    return f"Stopped {args.social_network}" if args.social_network else "Stopped all"


@app.get("/status")
async def get_status(args: GetTwitterStatusArgs):
    return {
        "running": running_loop,
        "running_social": running_social,
        "prompt": global_prompt,
        "last_time_checked_mentions": last_time_checked_twitter_mentions if args.social_network == "twitter" else None, #already preapred to add more socials
        "last_time_posted": last_time_posted_on_twitter if args.social_network == "twitter" else None, #already preapred to add more socials
        "agent_responses": responses[args.social_network]
    }


if __name__ == "__main__":
    logfire.info("Starting social API", _tags=["social_api"])
    try:
        uvicorn.run(app, host='localhost', port=int(os.getenv("SOCIAL_API_PORT")) or 42070)
    except KeyboardInterrupt:
        logfire.info("Social API stopped", _tags=["social_api"])
    except Exception as e:
        logfire.error(f"Error running social API: {e}", _tags=["social_api"])
        raise e
