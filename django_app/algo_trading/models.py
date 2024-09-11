from django.db import models
import uuid

# Create your models here.


class HistoricalData(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    ticker = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateTimeField('date published')
    open = models.DecimalField(max_digits=7, decimal_places=2)
    high = models.DecimalField(max_digits=7, decimal_places=2)
    low = models.DecimalField(max_digits=7, decimal_places=2)
    close = models.DecimalField(max_digits=7, decimal_places=2)
    total_traded_quantity = models.BigIntegerField(default=0)
