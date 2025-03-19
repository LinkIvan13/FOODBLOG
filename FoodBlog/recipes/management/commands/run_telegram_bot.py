from django.core.management.base import BaseCommand
from recipes.telegram_bot import run_bot

class Command(BaseCommand):
    help = 'Запускает Telegram-бота'

    def handle(self, *args, **kwargs):
        run_bot()
