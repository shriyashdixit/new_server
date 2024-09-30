# custom_management/management/commands/trigger_function.py

from django.core.management.base import BaseCommand
from algo_trading.views import get_live_data  # Import the function you want to trigger

class Command(BaseCommand):
    help = 'Triggers a function in views.py'

    def handle(self, *args, **kwargs):
        # Call the function
        get_live_data()  
        self.stdout.write(self.style.SUCCESS('Successfully triggered the function'))
