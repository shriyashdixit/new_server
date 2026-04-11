from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0005_bot_tracking_iprecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountrySummary',
            fields=[
            ],
            options={
                'verbose_name': 'Country Summary',
                'verbose_name_plural': 'Country Summary',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('upload.iprecord',),
        ),
    ]
