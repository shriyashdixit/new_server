from django.contrib import admin

# Register your models here.
from .models import HistoricalData


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    search_fields = ['ticker']
    list_display = ['ticker', 'date', 'open', 'high', 'low', 'close', 'total_traded_quantity']
