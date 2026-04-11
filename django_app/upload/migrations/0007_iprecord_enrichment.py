from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0006_countrysummary'),
    ]

    operations = [
        migrations.AddField(
            model_name='iprecord',
            name='hostname',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='iprecord',
            name='abuse_score',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='iprecord',
            name='abuse_total_reports',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
