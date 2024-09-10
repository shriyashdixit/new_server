from django.contrib import admin

# Register your models here.
from .models import HistoricalData


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ['date', 'open', 'high', 'low', 'close']
