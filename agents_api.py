from fastapi import FastAPI
import uvicorn
from utils.db import load_user_data, create_user_data, load_metrics, save_metrics
from langchain_core.messages import HumanMessage
import logfire
import os
from dotenv import load_dotenv

load_dotenv()

logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    service_name="agents_API",
    send_to_logfire="if-token-present",
    scrubbing=False
)

app = FastAPI()

user_data = load_user_data(logfire)

metrics = load_metrics()

@app.post("/prompt")
async def prompt(user_id: int, prompt: str):
    global user_data
    global metrics
    metrics['messages'] = metrics.get('messages', 0) + 1
    save_metrics(metrics)
    with logfire.span(
        f"Prompt from user {user_id}",
        user_id=user_id,
        _tags=['agents_api_prompt']
    ):
        try:
            for chunk in user_data[user_id].agent.stream(
                {"messages": [HumanMessage(content=prompt)]}, user_data[user_id].config
            ):
                if "agent" in chunk:
                    result = chunk["agent"]["messages"][0].content
                    logfire.info(
                        f"Agent response: {result}",
                        text=result,
                        user_id=user_id,
                        _tags=['agents_api_agent_response'])
                elif "tools" in chunk:
                    logfire.info(
                        f"Tool response: {chunk['tools']['messages'][0].content}",
                        text=chunk['tools']['messages'][0].content,
                        user_id=user_id,
                        _tags=['agents_api_tool_response'])
        
        except Exception as e:
            result = f'Error: {e}. You can try again or use the /cancel command to cancel the conversation.'
            logfire.error(
                f"Error: {e}",
                text=result,
                error=e,
                user_id=user_id,
                _tags=['agents_api_error'])
        return result

@app.post("/create_user")
async def create_user(user_id: int|str):
    global user_data
    user_data[int(user_id)] = create_user_data(int(user_id), logfire)
    return {"message": "User created"}
    
@app.get("/status")
async def get_status():
    return {
        "users": len(user_data.keys()),
        "messages": metrics['messages']
    }

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=int(os.getenv("AGENTS_API_PORT")) or 42071)


