from django.db import models

class TelegramMessage(models.Model):
    chat_id = models.BigIntegerField()  # Chat ID (can be for a group or private chat)
    message_id = models.BigIntegerField()  # Unique message ID
    user_id = models.BigIntegerField()  # Unique user ID of the sender
    username = models.CharField(max_length=255, null=True, blank=True)  # Optional username
    first_name = models.CharField(max_length=255, null=True, blank=True)  # Optional first name
    last_name = models.CharField(max_length=255, null=True, blank=True)  # Optional last name
    message_text = models.TextField(null=True, blank=True)  # The text content of the message
    date_sent = models.DateTimeField()  # Timestamp when the message was sent
    is_bot = models.BooleanField(default=False)  # Is the sender a bot
    chat_type = models.CharField(max_length=50, choices=[
        ('private', 'Private'),
        ('group', 'Group'),
        ('supergroup', 'Supergroup'),
        ('channel', 'Channel')
    ])  # Type of chat (private, group, etc.)
    reply_to_message_id = models.BigIntegerField(null=True, blank=True)  # If replying to another message
    location = models.JSONField(null=True, blank=True)  # Optional location data if the message has it
    attachments = models.JSONField(null=True, blank=True)  # Store any attachments (e.g., file URLs)

    def __str__(self):
        return f"Message from {self.username or self.user_id} in chat {self.chat_id}"
