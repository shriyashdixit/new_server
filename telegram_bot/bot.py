import os
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_KEY')

DJANGO_API_URL = 'http://web:8000/api/save_message/'  # Django app URL inside Docker network

# Start function for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot.")

# Function to handle received messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user

    # Data to send to Django
    data = {
        'message_id': message.message_id,
        'chat_id': message.chat_id,
        'message_text': message.text,
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_sent': message.date.isoformat(),
        'is_bot': user.is_bot,
        'chat_type': message.chat.type,
        'reply_to_message_id': message.reply_to_message.message_id if message.reply_to_message else None
    }

    print(data)  # Optional: For debugging

    # Make an asynchronous POST request to the Django app API
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(DJANGO_API_URL, json=data) as response:
                if response.status == 200:
                    await update.message.reply_text("Message saved successfully!")
                else:
                    await update.message.reply_text(f"Failed to save the message. Status code: {response.status}")
        except aiohttp.ClientError as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")


# Main function to initialize the bot
def main():
    # Initialize the Application with the bot token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handler for the /start command
    application.add_handler(CommandHandler('start', start))

    # Register message handler for handling text messages
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
