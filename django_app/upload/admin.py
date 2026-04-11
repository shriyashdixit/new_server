from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from .models import TelegramMessage, TelegramUser, ContactSubmission, PageVisit, IPRecord, CountrySummary


# ── Inlines ────────────────────────────────────────────────────────────────────

class PageVisitInline(admin.TabularInline):
    model = PageVisit
    fields = ['visited_at', 'path', 'country', 'city', 'user_agent']
    readonly_fields = ['visited_at', 'path', 'country', 'city', 'user_agent']
    extra = 0
    can_delete = False
    ordering = ['-visited_at']
    max_num = 20
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class ContactSubmissionInline(admin.TabularInline):
    model = ContactSubmission
    fields = ['submitted_at', 'name', 'email', 'service', 'is_bot']
    readonly_fields = ['submitted_at', 'name', 'email', 'service', 'is_bot']
    extra = 0
    can_delete = False
    ordering = ['-submitted_at']
    max_num = 20
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class TelegramMessageInline(admin.TabularInline):
    model = TelegramMessage
    fields = ['date_sent', 'message_text', 'chat_type']
    readonly_fields = ['date_sent', 'message_text', 'chat_type']
    extra = 0
    can_delete = False
    ordering = ['-date_sent']
    max_num = 20

    def has_add_permission(self, request, obj=None):
        return False


# ── Contact Submissions ────────────────────────────────────────────────────────

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submitted_at_display', 'is_bot_badge', 'name', 'email', 'company', 'service', 'country', 'city', 'isp', 'short_message']
    list_filter = ['is_bot', 'service', 'country', 'submitted_at']
    search_fields = ['name', 'email', 'company', 'message', 'country', 'city', 'isp']
    date_hierarchy = 'submitted_at'
    readonly_fields = ['name', 'email', 'phone', 'company', 'service', 'message',
                       'submitted_at', 'ip_address', 'city', 'region', 'country', 'isp', 'is_bot']
    ordering = ['-submitted_at']
    list_per_page = 100

    fieldsets = (
        ('Status', {
            'fields': ('is_bot',)
        }),
        ('Contact Details', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Enquiry', {
            'fields': ('service', 'message')
        }),
        ('Location', {
            'fields': ('ip_address', 'city', 'region', 'country', 'isp'),
        }),
        ('Meta', {
            'fields': ('submitted_at',),
            'classes': ('collapse',),
        }),
    )

    def submitted_at_display(self, obj):
        return obj.submitted_at.strftime('%d %b %Y, %H:%M:%S')
    submitted_at_display.short_description = 'Submitted At'
    submitted_at_display.admin_order_field = 'submitted_at'

    def is_bot_badge(self, obj):
        if obj.is_bot:
            return format_html('<span style="color:#c0392b;font-weight:700;">🤖 Bot</span>')
        return format_html('<span style="color:#27ae60;font-weight:700;">✅ Human</span>')
    is_bot_badge.short_description = 'Source'
    is_bot_badge.admin_order_field = 'is_bot'

    def short_message(self, obj):
        return obj.message[:80] + '…' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ── Page Visits ────────────────────────────────────────────────────────────────

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ['visited_at_display', 'path', 'ip_address', 'country', 'city', 'device_type', 'browser_summary', 'isp', 'referrer_display']
    list_filter = ['path', 'country', 'visited_at']
    date_hierarchy = 'visited_at'
    readonly_fields = ['path', 'referrer', 'user_agent', 'ip_address', 'city', 'region',
                       'country', 'isp', 'visited_at', 'device_type', 'browser_summary']
    ordering = ['-visited_at']
    search_fields = ['ip_address', 'referrer', 'country', 'city', 'isp']
    list_per_page = 100

    def visited_at_display(self, obj):
        return obj.visited_at.strftime('%d %b %Y, %H:%M:%S')
    visited_at_display.short_description = 'Visited At'
    visited_at_display.admin_order_field = 'visited_at'

    def referrer_display(self, obj):
        if not obj.referrer:
            return '—'
        return obj.referrer[:60] + '…' if len(obj.referrer) > 60 else obj.referrer
    referrer_display.short_description = 'Referrer'

    def browser_summary(self, obj):
        ua = obj.user_agent
        if 'Edg' in ua:
            return 'Edge'
        if 'Chrome' in ua:
            return 'Chrome'
        if 'Firefox' in ua:
            return 'Firefox'
        if 'Safari' in ua and 'Chrome' not in ua:
            return 'Safari'
        return ua[:30] if ua else '—'
    browser_summary.short_description = 'Browser'

    def device_type(self, obj):
        ua = obj.user_agent
        if any(kw in ua for kw in ('iPad', 'Tablet', 'tablet')):
            return 'Tablet'
        if any(kw in ua for kw in ('Mobile', 'Android', 'iPhone', 'iPod', 'BlackBerry', 'Windows Phone')):
            return 'Mobile'
        return 'Desktop' if ua else '—'
    device_type.short_description = 'Device'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ── IP Records ─────────────────────────────────────────────────────────────────

@admin.register(IPRecord)
class IPRecordAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'hostname_display', 'country', 'city', 'isp',
                    'abuse_badge', 'visit_count', 'form_submission_count',
                    'bot_submission_count', 'last_seen_display']
    list_filter = ['country', 'last_seen']
    search_fields = ['ip_address', 'hostname', 'country', 'city', 'isp']
    readonly_fields = ['ip_address', 'hostname', 'city', 'region', 'country', 'isp',
                       'abuse_score', 'abuse_total_reports', 'first_seen', 'last_seen',
                       'visit_count', 'form_submission_count', 'bot_submission_count', 'pages_hit_display']
    ordering = ['-last_seen']
    list_per_page = 100
    inlines = [PageVisitInline, ContactSubmissionInline]

    fieldsets = (
        ('IP Info', {
            'fields': ('ip_address', 'hostname', 'city', 'region', 'country', 'isp')
        }),
        ('Reputation', {
            'fields': ('abuse_score', 'abuse_total_reports'),
        }),
        ('Activity', {
            'fields': ('visit_count', 'form_submission_count', 'bot_submission_count', 'pages_hit_display')
        }),
        ('Timestamps', {
            'fields': ('first_seen', 'last_seen'),
        }),
    )

    def hostname_display(self, obj):
        if not obj.hostname:
            return '—'
        return obj.hostname[:60] + '…' if len(obj.hostname) > 60 else obj.hostname
    hostname_display.short_description = 'Hostname (PTR)'
    hostname_display.admin_order_field = 'hostname'

    def abuse_badge(self, obj):
        score = obj.abuse_score
        if score is None:
            return format_html('<span style="color:#999;">— no key</span>')
        if score >= 75:
            colour, label = '#c0392b', f'🔴 {score}%'
        elif score >= 25:
            colour, label = '#e67e22', f'🟡 {score}%'
        else:
            colour, label = '#27ae60', f'🟢 {score}%'
        return format_html('<span style="color:{};font-weight:700;">{}</span>', colour, label)
    abuse_badge.short_description = 'Abuse Score'
    abuse_badge.admin_order_field = 'abuse_score'

    def first_seen_display(self, obj):
        return obj.first_seen.strftime('%d %b %Y, %H:%M:%S')
    first_seen_display.short_description = 'First Seen'
    first_seen_display.admin_order_field = 'first_seen'

    def last_seen_display(self, obj):
        return obj.last_seen.strftime('%d %b %Y, %H:%M:%S')
    last_seen_display.short_description = 'Last Seen'
    last_seen_display.admin_order_field = 'last_seen'

    def pages_hit_display(self, obj):
        pages = obj.pages_hit or {}
        if not pages:
            return '—'
        rows = ''.join(
            f'<tr><td style="padding:2px 12px 2px 0"><code>{path}</code></td>'
            f'<td><b>{count}</b></td></tr>'
            for path, count in sorted(pages.items(), key=lambda x: -x[1])
        )
        return format_html('<table>{}</table>', format_html(rows))
    pages_hit_display.short_description = 'Pages Hit'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ── Country Summary ────────────────────────────────────────────────────────────

@admin.register(CountrySummary)
class CountrySummaryAdmin(admin.ModelAdmin):
    """Aggregated view: one row per country with totals."""
    change_list_template = 'admin/country_summary_changelist.html'
    list_per_page = 100

    def changelist_view(self, request, extra_context=None):
        rows = (
            IPRecord.objects
            .values('country')
            .annotate(
                total_visits=Sum('visit_count'),
                unique_ips=Count('id'),
                total_form_submissions=Sum('form_submission_count'),
                total_bot_submissions=Sum('bot_submission_count'),
            )
            .order_by('-total_visits')
        )
        extra_context = extra_context or {}
        extra_context['summary_rows'] = rows
        extra_context['title'] = 'Country Summary'
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ── Telegram models ────────────────────────────────────────────────────────────

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    search_fields = ['user_id']
    list_display = ['chat_id', 'message_id', 'user_id', 'username', 'first_name', 'last_name', 'message_text']
    list_per_page = 100


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    search_fields = ['username']
    list_display = ['username', 'user_id', 'chat_id']
    list_per_page = 100
    inlines = [TelegramMessageInline]
