from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from utils.speech import download_voice_message, transcribe_audio
from langchain_core.messages import HumanMessage
from main import initialize_agent

from dotenv import load_dotenv
import logging
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi! Say something, I will respond.')
    return 'continue'

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Conversation cancelled. You can start a new one with the /start command.')
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global agent_executor
    global config
    msg = await update.effective_message.reply_html('<i>Thinking...</i>')

    try:
        # Handle voice messages
        if update.message.voice:
            await msg.edit_text('<i>Transcribing audio...</i>', parse_mode='HTML')
            # Get the voice file
            voice_file = await update.message.voice.get_file()
            # Download the voice file
            voice_path = await download_voice_message(voice_file.file_path)
            # Transcribe the audio
            text = await transcribe_audio(voice_path)
            await msg.edit_text(f'<i>Transcribed: "{text}"</i>\n\n<i>Give me a moment, please...</i>', parse_mode='HTML')
        else:
            text = update.effective_message.text

        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=text)]}, config
        ):
            if "agent" in chunk:
                result = chunk["agent"]["messages"][0].content
            elif "tools" in chunk:
                print(chunk["tools"]["messages"][0].content)
        
    except Exception as e:
        result = f'Error: {e}. You can try again or use the /cancel command to cancel the conversation.'
    
    await msg.edit_text(result, parse_mode='markdown', disable_web_page_preview=True)
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

agent_executor, config = initialize_agent()

#async def return_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.effective_chat.send_message(f'Your chat id is {update.effective_chat.id}')

def main():
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(conversation_handler)
    #application.add_handler(MessageHandler(filters.TEXT, return_chat_id))
    application.run_polling(timeout=60, read_timeout=60, write_timeout=60, connect_timeout=60, pool_timeout=60)

if __name__ == "__main__":
    main()
