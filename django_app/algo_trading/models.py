from django.db import models

# Create your models here.


class HistoricalData(models.Model):
    date = models.DateTimeField('date published')
    open = models.DecimalField(max_digits=7, decimal_places=5)
    high = models.DecimalField(max_digits=7, decimal_places=5)
    low = models.DecimalField(max_digits=7, decimal_places=5)
    close = models.DecimalField(max_digits=7, decimal_places=5)
