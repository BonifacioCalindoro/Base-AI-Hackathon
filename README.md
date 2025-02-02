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

Create an account on https://cdp.coinbase.com/ and create an API key with all permissions.
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

Create a bot on https://t.me/BotFather and get the token.
Then, create a channel/group, add the bot to it and get the chat id (or you can directly use your personal chat id).
Then, set the following environment variable:

```bash
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-desired-telegram-chat-id
```

### Logfire Token (Optional)

Create an account on https://logfire.pydantic.dev/, create a new project and get a Write token for it.
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

This project leverages Logfire, which is a tool for telemetry and observability. It is highly recommended to use it, as it will help you debug the agent and understand its behavior. You can also create dashboards to monitor the agent's performance.

## Telegram Bot

To interact with the agent, just start sending a message to it or send a voice message. It will respond to you with natural language.

## Example interaction:

```
Hello, I want to buy USDC with 0.001 ETH
```
And it would buy USDC with 0.001 ETH.


```
Hello, I want to sell all my USDC for ETH
```
And it would sell all the USDC in its wallet for ETH.

```
Hey, i want you to find a good pool for this contract address: 0x0555e30da8f98308edb960aa94c0db47230d2b9c

Then open an aggressive rsi with 0.0001ETH per buy, on 15m timeframes
```
And it would start the rsi strategy with those parameters.

```
Close the rsi now
```
And it would stop the rsi strategy.


```
Can you buy SuperAgent42.base.eth for me?
```
And it would claim the BaseName and mint it to its wallet.