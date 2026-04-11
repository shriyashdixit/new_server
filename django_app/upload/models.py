from django.db import models


class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=255, blank=True)
    service = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    isp = models.CharField(max_length=255, blank=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'

    def __str__(self):
        return f"{self.name} <{self.email}>"


class PageVisit(models.Model):
    path = models.CharField(max_length=500)
    referrer = models.CharField(max_length=2000, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    isp = models.CharField(max_length=255, blank=True)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visited_at']
        verbose_name = 'Page Visit'
        verbose_name_plural = 'Page Visits'

    def __str__(self):
        return f"{self.path} — {self.visited_at.strftime('%d %b %Y %H:%M')}"


class IPRecord(models.Model):
    """One row per unique IP — running totals of activity across the site."""
    ip_address = models.GenericIPAddressField(unique=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    isp = models.CharField(max_length=255, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    hostname = models.CharField(max_length=500, blank=True)       # reverse DNS
    abuse_score = models.SmallIntegerField(null=True, blank=True)  # 0–100, None = not checked
    abuse_total_reports = models.PositiveIntegerField(null=True, blank=True)
    visit_count = models.PositiveIntegerField(default=0)
    form_submission_count = models.PositiveIntegerField(default=0)
    bot_submission_count = models.PositiveIntegerField(default=0)
    pages_hit = models.JSONField(default=dict)  # {'/': 5, '/contact/': 2}

    class Meta:
        ordering = ['-last_seen']
        verbose_name = 'IP Record'
        verbose_name_plural = 'IP Records'

    def __str__(self):
        return f"{self.ip_address} ({self.country or '?'})"


class CountrySummary(IPRecord):
    """Proxy model — used only for the grouped Country Summary admin view."""
    class Meta:
        proxy = True
        verbose_name = 'Country Summary'
        verbose_name_plural = 'Country Summary'


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

class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    chat_id = models.BigIntegerField()

    def __str__(self):
        return self.username
