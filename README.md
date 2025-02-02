# AI Blockchain Agent

This is an AI agent that can be used to trade on the blockchain. It is built using CDP Agentkit and langchain, and leverages Telegram for communication with the user and FastAPI to handle the RSI auto trading strategy backend.

## Installation and Setup

```bash
git clone https://github.com/BonifacioCalindoro/Base-AI-Hackathon
cd Base-AI-Hackathon
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
```

### Coinbase API Key

Create an account on Coinbase Developer Platform and create an API key with all permissions.
Then, set the following environment variables:

```bash
CDP_API_KEY_NAME=your-api-key-name
CDP_API_KEY_PRIVATE_KEY=your-api-key-private-key
```

after doing this, you need to create a wallet, which you can do with the create_wallet.py script.

```bash
python create_wallet.py
```

after doing so, it is highly recommended to save a backup of the wallet.json file in a secure location, as it contains the private key of your wallet.

### OpenAI API Key

Create an account on OpenAI and create an API key.
Then, set the following environment variable:

```bash
OPENAI_API_KEY=your-openai-api-key
```

### Telegram Bot Token

Create a bot on t.me/BotFather and get the token.
Then, create a channel/group, add the bot to it and get the chat id (or you can directly use your personal chat id).
Then, set the following environment variable:

```bash
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-desired-telegram-chat-id
```

### Logfire Token (Optional)

Create an account on logfire.pydantic.dev, create a new project and get a Write token for it.
Then, set the following environment variable:

```bash
LOGFIRE_TOKEN=your-logfire-token
```

## Usage

```bash
python bot.py
python api.py
```

both services need to be running to use the agent


## Logging

This project leverages Logfire for logging. You can find the token in the Logfire dashboard at logfire.pydantic.dev

## Telegram Bot

To interact with the agent, just start sending a message to it or send a voice message. It will respond to you.