from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0003_contactsubmission_pagevisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsubmission',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='contactsubmission',
            name='region',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='contactsubmission',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='contactsubmission',
            name='isp',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='region',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='isp',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
