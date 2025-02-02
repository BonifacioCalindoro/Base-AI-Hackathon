#AI Blockchain Agent

This is an AI agent that can be used to trade on the blockchain. It is built using CDP Agentkit and langchain, and leverages Telegram for communication with the user and FastAPI to handle the RSI auto trading strategy backend.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python bot.py
python api.py
```

both services need to be running to use the agent

## Configuration

```bash
cp .env.example .env
```

## Logging

This project leverages Logfire for logging. You can find the token in the Logfire dashboard at logfire.pydantic.dev

## Telegram Bot

To interact with the agent, just start sending a message to it or send a voice message. It will respond to you.