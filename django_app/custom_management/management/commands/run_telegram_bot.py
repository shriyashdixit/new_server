import logging
from django.core.management.base import BaseCommand
from telegram.ext import Updater, CommandHandler
from django.conf import settings

token = settings.TELEGRAM_BOT_KEY
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **kwargs):
        # Initialize the bot and its dispatcher
        updater = Updater(token, use_context=True)
        dispatcher = updater.dispatcher

        # Define command handlers
        def start(update, context):
            update.message.reply_text("Hello world!")

        def help(update, context):
            update.message.reply_text("""
            The following commands are available:

            /start -> Welcome to the channel
            /help -> This message
             """)


        # Register command handlers
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('help', help))
        
        # More command handlers (add other command handlers here)

        # Start polling
        updater.start_polling()
        updater.idle()

        logger.info("Bot started polling...")
