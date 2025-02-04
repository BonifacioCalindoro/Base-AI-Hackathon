from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from utils.speech import download_voice_message, transcribe_audio
from langchain_core.messages import HumanMessage
from agent import initialize_agent
import httpx
from dotenv import load_dotenv
import logging
import os
import logfire

load_dotenv()

logfire.configure(
    token=os.getenv('LOGFIRE_TOKEN'),
    service_name='telegram_bot',
    send_to_logfire='if-token-present',
    scrubbing=False
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

main_agent_executor, main_agent_config = initialize_agent()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print(user_id)
    username = update.effective_user.username
    logfire.info(
        f"/start command received",
        user_id=user_id,
        _tags=['bot_start'])
    if username != os.getenv('TELEGRAM_ADMIN_USERNAME'):
        if user_id not in os.listdir("data/users"):
            msg = await update.effective_message.reply_text('<i>Creating agent...</i>', parse_mode='HTML')
            response = await httpx.AsyncClient(timeout=30).post(f"http://localhost:{os.getenv('AGENTS_API_PORT')}/create_user", params={"user_id": user_id})
            await msg.edit_text('<i>Agent created!</i>\n<i>You can now start a conversation with me.</i>', parse_mode='HTML')
        else:
            await update.message.reply_text('Hi! Say something, I will respond.')
    else:
        await update.message.reply_text('Hi! Say something, I will respond.')
    return 'continue'

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logfire.info(
        f"/cancel command received",
        _tags=['bot_cancel'])
    await update.message.reply_text('Conversation cancelled. You can start a new one with the /start command.')
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global main_agent_executor
    global main_agent_config
    user_id = update.effective_user.id
    with logfire.span(
        f"Handling message",
        _tags=['bot_handle_message']
    ):
        msg = await update.effective_message.reply_html('<i>Thinking...</i>')
        # Handle voice messages
        if update.message.voice:
            await msg.edit_text('<i>Transcribing audio...</i>', parse_mode='HTML')
            # Get the voice file
            voice_file = await update.message.voice.get_file()
            # Download the voice file
            voice_path = await download_voice_message(voice_file.file_path)
            # Transcribe the audio
            text = await transcribe_audio(voice_path)
            logfire.info(
                f"Transcribed message: {text}",
                text=text,
                user_id=user_id,
                _tags=['bot_transcribe_message'])
            await msg.edit_text(f'<i>Transcribed: "{text}"</i>\n\n<i>Give me a moment, please...</i>', parse_mode='HTML')
        else:
            text = update.effective_message.text
            logfire.info(
                f"Received message: {text}",
                text=text,
                user_id=user_id,
                _tags=['bot_receive_message'])
        
        if update.effective_user.username == os.getenv('TELEGRAM_ADMIN_USERNAME'):
            try:
                for chunk in main_agent_executor.stream(
                    {"messages": [HumanMessage(content=text)]}, main_agent_config
                ):
                    if "agent" in chunk:
                        result = chunk["agent"]["messages"][0].content
                        logfire.info(
                            f"Agent response: {result}",
                            text=result,
                            user_id='ADMIN',
                            _tags=['bot_agent_response'])
                    elif "tools" in chunk:
                        print(chunk["tools"]["messages"][0].content)
                        logfire.info(
                            f"Tool response: {chunk['tools']['messages'][0].content}",
                            text=chunk['tools']['messages'][0].content,
                            user_id='ADMIN',
                            _tags=['bot_tool_response'])
            
            except Exception as e:
                result = f'Error: {e}. You can try again or use the /cancel command to cancel the conversation.'
                logfire.error(
                    f"Error: {e}",
                    text=result,
                    error=e,
                    user_id='ADMIN',
                    _tags=['bot_error'])
        else:
            result = (await httpx.AsyncClient(timeout=120).post(f"http://localhost:{os.getenv('AGENTS_API_PORT')}/prompt", params={"user_id": user_id, "prompt": text})).json()
            logfire.info(
                f"Agent response: {result}",
                text=result,
                user_id=user_id,
                _tags=['bot_agent_response'])
        try:
            await msg.edit_text(result, parse_mode='markdown', disable_web_page_preview=True)
        except Exception as e:
            logfire.info(
                f"Error editing message, retrying without markdown: {e}",
                error=e,
                text=result,
                user_id=user_id,
                _tags=['bot_error_editing_message'])
            try:
                await msg.edit_text(result)
            except Exception as e:
                logfire.error(
                    f"Error editing message: {e}",
                    error=e,
                    text=result,
                    user_id=user_id,
                    _tags=['bot_error_editing_message'])
                result = f'There was an unexpected error! Please try again later.'
                await msg.edit_text(result)
        logfire.info(
            f"Agent final response: {result}",
            text=result,
            user_id=user_id,
            _tags=['bot_agent_final_response'])
    return 'continue'

conversation_handler = ConversationHandler(
    entry_points=[
            MessageHandler(
                filters.TEXT & ~filters.COMMAND | filters.VOICE, 
                handle_message
            )
        ],
    states={
        'continue': [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND | filters.VOICE, 
                handle_message
            )
        ]
    },
    fallbacks=[CommandHandler(['cancel', 'exit', 'stop'], cancel)],
    allow_reentry=False
)

#async def return_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.effective_chat.send_message(f'Your chat id is {update.effective_chat.id}')

def main():
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).connect_timeout(60).read_timeout(60).write_timeout(60).pool_timeout(60).build() #What an ugly line of code, but they say DeprecationWarning so... 
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conversation_handler)
    #application.add_handler(MessageHandler(filters.TEXT, return_chat_id))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    logfire.info(
        f"Starting bot",
        _tags=['bot_start'])
    main()