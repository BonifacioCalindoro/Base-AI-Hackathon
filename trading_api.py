from fastapi import FastAPI, BackgroundTasks
import uvicorn 
from models.trading_strategies import StartRSIArgs, StopRSIArgs, StartRSIResponse, StopRSIResponse
import asyncio
from tools.trading_indicators import get_ohlcv_data_and_calculate_rsi_with_ohlcv
import os
from dotenv import load_dotenv
from cdp_langchain.utils import CdpAgentkitWrapper
from telegram import Bot
import logfire

load_dotenv()

logfire.configure(
    token=os.getenv('LOGFIRE_TOKEN'),
    service_name='rsi-backend',
    send_to_logfire='if-token-present',
    scrubbing=False
)


bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

app = FastAPI()

global_strategy_runners = {
    'ping pong': False
}

strategies_to_rsi_mappigs = {
    'aggressive': {
        'buy': 35,
        'sell': 65
    },
    'medium': {
        'buy': 30,
        'sell': 70
    },
    'conservative': {
        'buy': 25,
        'sell': 75
    }
}

wallet_data_file = 'wallet.json'

wallet_data = None

if os.path.exists(wallet_data_file):
    with open(wallet_data_file) as f:
        wallet_data = f.read()

with open('.env', 'r') as f:
    for line in f:
        if line.startswith('CDP_API_KEY_PRIVATE_KEY='):
            raw_key = line[len('CDP_API_KEY_PRIVATE_KEY='):].strip() # This was necessary because python-dotenv was not able to parse the key correctly
            break
    
values = {
    "cdp_api_key_name": os.getenv("CDP_API_KEY_NAME"),
    "cdp_api_key_private_key": raw_key.replace('\\n', '\n'),
}

if wallet_data is not None:
    values["cdp_wallet_data"] = wallet_data
else:
    raise Exception("No wallet data found")

agentkit = CdpAgentkitWrapper(**values)
wallet = agentkit.wallet

async def send_message(message: str):
    with logfire.span(
        f"Sending message to Telegram",
        message=message,
        _tags=['api_send_message']
    ):
        message_object = await bot.send_message(chat_id=os.getenv('REPORTS_CHAT_ID'), text=message, parse_mode='HTML')
        logfire.info(
            f"Message sent to Telegram",
            message=message,
            message_id=message_object.message_id,
            _tags=['api_send_message_success'])
    return message_object

async def edit_message(message_id: int, message: str):
    with logfire.span(
        f"Editing message in Telegram",
        message=message,
        message_id=message_id,
        _tags=['api_edit_message']
    ):
        await bot.edit_message_text(chat_id=os.getenv('REPORTS_CHAT_ID'), message_id=message_id, text=message, parse_mode='HTML')

async def pin_message(message_id: int):
    await bot.pin_chat_message(chat_id=os.getenv('REPORTS_CHAT_ID'), message_id=message_id)

async def unpin_message(message_id: int):
    await bot.unpin_chat_message(chat_id=os.getenv('REPORTS_CHAT_ID'), message_id=message_id)

async def rsi_runner(args: StartRSIArgs, strategy_id: str = 'ping pong'):
    global global_strategy_runners
    rsi_list = []
    already_bought = False
    already_sold = True
    buys, sells, current_profit = 0, 0, 0
    last_bought = 0
    current_message = ""
    global_strategy_runners[strategy_id] = True
    logfire.info(
        f"Starting RSI strategy with ID: {strategy_id}",
        args=args,
        strategy_id=strategy_id,
        _tags=['rsi_start', 'ping_pong_start'])
    message_to_send = (
        "<u>🤖 Starting RSI ping pong strategy 🏓</u>\n\n"
        f"📝 CA: <code>{args.contract_address}</code>\n"
        f"🏊 Pool: <code>{args.pool_address}</code>\n" 
        f"⏱️ RSI timeframe: <code>{args.timeframe}</code>\n"
        f"📊 RSI period: <code>{args.period}</code>\n"
        f"💰 Buy amount: <code>{args.amount_for_each_buy}</code>\n"
        f"📈 Strategy type: <code>{args.strategy_type}</code>\n"
    )
    message_to_send += (
        f"📉 Price range low: <code>{args.price_range_low}</code>\n"
    ) if args.price_range_low is not None else ''
    message_to_send += (
        f"📈 Price range high: <code>{args.price_range_high}</code>\n"
    ) if args.price_range_high is not None else ''
    message_to_send += (
        f"🔢 Custom RSI for buy: <code>{args.rsi_for_custom_strategy_buy}</code>\n"
        f"🔢 Custom RSI for sell: <code>{args.rsi_for_custom_strategy_sell}</code>") if args.strategy_type == 'custom' else ''
    current_message = message_to_send
    message_object = await send_message(message_to_send)
    await pin_message(message_object.message_id)
    if args.strategy_type == 'custom':
        buy_rsi = args.rsi_for_custom_strategy_buy
        sell_rsi = args.rsi_for_custom_strategy_sell
    else:
        buy_rsi = strategies_to_rsi_mappigs[args.strategy_type]['buy']
        sell_rsi = strategies_to_rsi_mappigs[args.strategy_type]['sell']
    while True:
        if global_strategy_runners[strategy_id] is False:
            current_message = current_message + "\n🛑 Strategy stopped"
            await send_message(f"🤖 Strategy stopped")
            await edit_message(message_object.message_id, current_message)
            break
        current_rsi, ohlcv_data = get_ohlcv_data_and_calculate_rsi_with_ohlcv(args.pool_address, args.timeframe, args.period)
        if args.price_range_low is not None:
            if ohlcv_data.data.attributes.ohlcv_list[-1][4] < args.price_range_low:
                logfire.info(
                    f"Price out of range (low) for {args.contract_address} ({ohlcv_data.data.attributes.ohlcv_list[-1][4]}). Strategy {strategy_id} stopped",
                    args=args,
                    strategy_id=strategy_id,
                    price=ohlcv_data.data.attributes.ohlcv_list[-1][4],
                    _tags=['rsi_stop', 'out_of_range_low'])
                await send_message(f"🤖 Price out of range (low) for {args.contract_address} ({ohlcv_data.data.attributes.ohlcv_list[-1][4]})\n🤖 Strategy {strategy_id} stopped")
                current_message = current_message + "\n\n🤖 Price out of range (low) for {args.contract_address} ({ohlcv_data.data.attributes.ohlcv_list[-1][4]})\n🤖 Strategy {strategy_id} stopped"
                await edit_message(message_object.message_id, current_message)
                break
        if args.price_range_high is not None:
            if ohlcv_data.data.attributes.ohlcv_list[-1][4] > args.price_range_high:
                logfire.info(
                    f"Price out of range (high) for {args.contract_address} ({ohlcv_data.data.attributes.ohlcv_list[-1][4]}). Strategy {strategy_id} stopped",
                    args=args,
                    strategy_id=strategy_id,
                    price=ohlcv_data.data.attributes.ohlcv_list[-1][4],
                    _tags=['rsi_stop', 'out_of_range_high'])
                await send_message(f"🤖 Price out of range (high) for {args.contract_address} ({ohlcv_data.data.attributes.ohlcv_list[-1][4]})\n🤖 Strategy {strategy_id} stopped")
                current_message = current_message + "\n\n🤖 Price out of range (high) for {args.contract_address} ({ohlcv_data.data.attributes.ohlcv_list[-1][4]})\n🤖 Strategy {strategy_id} stopped"
                await edit_message(message_object.message_id, current_message)
                break
        logfire.info(
            f"Current RSI: {current_rsi.rsi}",
            args=args,
            strategy_id=strategy_id,
            rsi=current_rsi.rsi,
            _tags=['rsi_current'])
        rsi_list.append(current_rsi.rsi)
        if len(rsi_list) > 1 and rsi_list[-2] > rsi_list[-1]:
            direction = 'down'
        elif len(rsi_list) > 1 and rsi_list[-2] < rsi_list[-1]:
            direction = 'up'
        else:
            direction = 'neutral'
        logfire.info(
            f"Direction: {direction}",
            args=args,
            strategy_id=strategy_id,
            direction=direction,
            _tags=['rsi_direction'])
        if rsi_list[-1] < buy_rsi and not already_bought:
            with logfire.span(
                f"Buying {args.contract_address}",
                args=args,
                strategy_id=strategy_id,
                _tags=['rsi_buy']
            ):
                try:
                    result = wallet.trade(
                        amount=args.amount_for_each_buy,
                        from_asset_id="eth",
                        to_asset_id=args.contract_address
                    )
                    last_bought = result.to_amount
                    tx_hash = result.transaction.transaction_hash
                    logfire.info(
                        f"Trade result: {result}",
                        args=args,
                        strategy_id=strategy_id,
                        amount=last_bought,
                        tx_hash=tx_hash,
                        _tags=['rsi_buy_result'])
                    already_bought = True
                    already_sold = False
                    buys += 1
                    await send_message(f"🤖 Bought <b>{last_bought}</b> of <code>{args.contract_address}</code> with tx hash <code>{tx_hash}</code>")
                    if 'Buys: ' in current_message:
                        buys_part = current_message.split('Buys: ')[1].split('\n')[0]
                        current_message = current_message.replace('Buys: ' + buys_part, f'Buys: {buys}')
                    else:
                        current_message = current_message + f"\n\n🤖 Buys: {buys}"
                    await edit_message(message_object.message_id, current_message)

                except Exception as e:
                    logfire.error(
                        f"Error buying {args.contract_address}: {e}",
                        args=args,
                        strategy_id=strategy_id,
                        _tags=['rsi_buy_error'])
                    await send_message(f"🤖 Error buying <code>{args.contract_address}</code>: {e}\n🤖 Strategy {strategy_id} stopped")
                    current_message = current_message + f"\n\n🤖 Error buying <code>{args.contract_address}</code>: {e}\n🤖 Strategy {strategy_id} stopped"
                    await edit_message(message_object.message_id, current_message)
                    global_strategy_runners[strategy_id] = False
                    return
                    #raise e
        elif rsi_list[-1] > sell_rsi and not already_sold:
            with logfire.span(
                f"Selling {args.contract_address}",
                args=args,
                strategy_id=strategy_id,
                _tags=['rsi_sell']
            ):
                try:
                    result = wallet.trade(
                        amount=last_bought,
                        from_asset_id=args.contract_address,
                        to_asset_id="eth"
                    )
                    got_profit = float(result.to_amount) - float(args.amount_for_each_buy)
                    tx_hash = result.transaction.transaction_hash
                    logfire.info(
                        f"Trade result: {result}",
                        args=args,
                        strategy_id=strategy_id,
                        amount=last_bought,
                        profit=got_profit,
                        tx_hash=tx_hash,
                        _tags=['rsi_sell_result'])
                    already_sold = True
                    already_bought = False
                    await send_message(f"🤖 Sold <b>{last_bought}</b> of <code>{args.contract_address}</code> with tx hash <code>{tx_hash}</code>\n\n💰 Profit: <b>{got_profit}</b> ETH")
                    sells += 1
                    if 'Sells: ' in current_message:
                        sells_part = current_message.split('Sells: ')[1].split('\n')[0]
                        current_message = current_message.replace('Sells: ' + sells_part, f'Sells: {sells}')
                    else:
                        current_message = current_message + f"\n🤖 Sells: {sells}"
                    await edit_message(message_object.message_id, current_message)
                except Exception as e:
                    logfire.error(
                        f"Error selling {args.contract_address}: {e}",
                        args=args,
                        strategy_id=strategy_id,
                        _tags=['rsi_sell_error'])
                    await send_message(f"🤖 Error selling <code>{args.contract_address}</code>: {e}\n🤖 Strategy {strategy_id} stopped")
                    current_message = current_message + "\n\n🤖 Error selling <code>{args.contract_address}</code>: {e}\n🤖 Strategy {strategy_id} stopped"
                    await edit_message(message_object.message_id, current_message)
                    global_strategy_runners[strategy_id] = False
                    return
                    #raise e
        else:
            print(f"No action needed for {args.contract_address}")
        await asyncio.sleep(10)
        

@app.post("/start_rsi_strategy")
async def start_rsi_strategy(args: StartRSIArgs, background_tasks: BackgroundTasks):
    background_tasks.add_task(rsi_runner, args, 'ping pong')
    logfire.info(
        f"Starting RSI strategy with ID: ping pong",
        args=args,
        strategy_id='ping pong',
        _tags=['api_start_rsi_strategy'])
    return StartRSIResponse(strategy_id='ping pong', success=True).model_dump()

@app.post("/stop_rsi_strategy")
async def stop_rsi_strategy(args: StopRSIArgs, background_tasks: BackgroundTasks):
    global global_strategy_runners
    logfire.info(
        f"Stopping RSI strategy with ID: {'ping pong'}",
        args=args,
        strategy_id='ping pong',
        _tags=['api_stop_rsi_strategy'])
    global_strategy_runners['ping pong'] = False
    return StopRSIResponse(success=True).model_dump()

if __name__ == "__main__":
    logfire.info(
        f"Starting API",
        _tags=['api_start'])
    uvicorn.run(app, host="localhost", port=int(os.getenv('TRADING_API_PORT')) or 42069)