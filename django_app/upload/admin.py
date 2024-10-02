from django.contrib import admin
# Register your models here.
from .models import TelegramMessage, TelegramUser


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    search_fields = ['user_id']
    list_display = ['chat_id', 'message_id', 'user_id', 'username', 'first_name', 'last_name', 'message_text']

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    search_fields = ['username']
    list_display = ['username', 'user_id', 'chat_id']
