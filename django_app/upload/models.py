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
    ip_record = models.ForeignKey(
        'IPRecord', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='contact_submissions',
    )

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
    ip_record = models.ForeignKey(
        'IPRecord', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='page_visits',
    )

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


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('backend', 'Backend Engineering'),
        ('ai', 'AI Automation'),
        ('aws', 'AWS Cloud'),
        ('security', 'Security'),
        ('devops', 'DevOps'),
        ('llm', 'LLM & GenAI'),
    ]
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=320)
    excerpt = models.TextField(help_text='Short summary shown on the blog list page.')
    content = models.TextField(help_text='Full article body — HTML is supported.')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    published_at = models.DateField(null=True, blank=True, help_text='Leave blank while drafting.')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title


class CaseStudy(models.Model):
    CATEGORY_CHOICES = [
        ('backend', 'Backend'),
        ('ai', 'AI & ML'),
        ('cloud', 'Cloud'),
        ('devops', 'DevOps'),
        ('llm', 'LLM'),
    ]
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=320)
    description = models.TextField(help_text='Short description shown on the work list page.')
    body = models.TextField(
        blank=True,
        help_text='Full case study content for the detail page — HTML is supported.'
    )
    categories = models.CharField(
        max_length=200,
        help_text='Space-separated filter tokens matching the filter buttons, e.g. "backend ai"'
    )
    tags = models.JSONField(
        default=list,
        help_text='JSON list of display tags, e.g. ["Django", "Python", "Cloud Backend"]'
    )
    thumb_html = models.TextField(
        blank=True,
        help_text='HTML for the card thumbnail area (icon images / badges). Rendered unescaped.'
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Lower number = shown first.')

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'

    def __str__(self):
        return self.title


class JobListing(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, help_text='e.g. "Pune, India" or "Remote"')
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='full-time')
    description = models.TextField(help_text='Role description shown on the careers page — HTML is supported.')
    requirements = models.TextField(blank=True, help_text='Requirements list — HTML is supported.')
    is_open = models.BooleanField(default=True, help_text='Uncheck to close the role without deleting it.')
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']
        verbose_name = 'Job Listing'
        verbose_name_plural = 'Job Listings'

    def __str__(self):
        status = 'Open' if self.is_open else 'Closed'
        return f'{self.title} [{status}]'


class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, help_text='Display role shown on the team card.')
    bio = models.TextField()
    tags = models.JSONField(
        default=list,
        help_text='JSON list of skill tags, e.g. ["Backend Architecture", "AI Automation"]'
    )
    avatar_initial = models.CharField(
        max_length=10,
        help_text='Letter(s) or emoji shown in the avatar circle, e.g. "S" or "✦"'
    )
    is_ai_partner = models.BooleanField(
        default=False,
        help_text='Apply the AI-partner card style (dim gradient, ✦ badge).'
    )
    order = models.PositiveIntegerField(default=0, help_text='Lower number = shown first.')
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return self.name


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
    sender = models.ForeignKey(
        'TelegramUser', null=True, blank=True, on_delete=models.SET_NULL,
        to_field='user_id', related_name='messages',
    )

    def __str__(self):
        return f"Message from {self.username or self.user_id} in chat {self.chat_id}"

class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    chat_id = models.BigIntegerField()

    def __str__(self):
        return self.username
