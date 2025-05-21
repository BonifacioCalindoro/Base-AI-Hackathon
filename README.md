# AI Blockchain Agent for Base

This is an AI agent that can be used to trade on the blockchain. It is built using CDP Agentkit and langchain, and leverages Telegram for communication with the user and FastAPI to handle the RSI auto trading strategy backend.

UPGRADED TO ONE_TO_MANY model! So you can run one instance on the bot, and let other users interact with it through telegram while separating each user's data and wallets.

Don't want to run your own instance, or don't know how to? You can still use a lite version (without social agent or autotrading backend) at https://t.me/BaseSuperAss_bot

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
TELEGRAM_ADMIN_USERNAME=your-telegram-username
```

### Logfire Token (Optional)

Create an account on https://logfire.pydantic.dev/, create a new project and get a Write token for it.
Then, set the following environment variable:

```bash
LOGFIRE_TOKEN=your-logfire-token
```

### Twitter API 

create an X account, go to https://developer.x.com/en/portal/dashboard and create a new project, then create an app and get the credentials.
Then, set the following environment variables:

```bash
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=
```

IMPORTANT: even though you don't need to use OAUTH 2.0, you need to edit the app's permissions to read and write to your timeline. It will ask for valid URLs but you can put any valid URL there.
After doing so, you need to refresh the twitter access tokens and put them in the .env file.

## Usage

```bash
python bot.py
python trading_api.py
python social_api.py
python agents_api.py
```

all services need to be running to use all the features of the agent. You can use the "screen" apt package to run the services in the background.

```bash
sudo apt install screen
```

```bash
screen -S bot
python bot.py
```
press Ctrl+A + D to detach from the screen.

```bash
screen -S trading_api
python trading_api.py
```
press Ctrl+A + D to detach from the screen.

```bash
screen -S social_api
python social_api.py
```
press Ctrl+A + D to detach from the screen.

```bash
screen -S agents_api
python agents_api.py
```
press Ctrl+A + D to detach from the screen.

To reattach to any screen, just use the following command:

```bash
screen -r <screen-name>
```

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

```
Start the twitter agent
```
And it would start the twitter agent with the default prompt.

```
Stop the twitter agent
```
And it would stop the twitter agent.

```
Start the twitter agent with prompt "Post on twitter about how cool SuperAssistant is!"
```
And it would start the twitter agent with that custom prompt.

## Funding

## ☕ Sponsor Me

If you like this project, consider [buying me OpenAI credits](https://buymeacoffee.com/bonifaciocalindoro)!

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=bonifaciocalindoro&button_colour=FFDD00&font_colour=000000&font_family=Comic&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/bonifaciocalindoro)

```
Get the status of the twitter agent
```
And it would return the status of the twitter agent's latest actions.
