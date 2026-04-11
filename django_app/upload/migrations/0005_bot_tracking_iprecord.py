from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0004_geo_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsubmission',
            name='is_bot',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='IPRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('region', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('isp', models.CharField(blank=True, max_length=255)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now_add=True)),
                ('visit_count', models.PositiveIntegerField(default=0)),
                ('form_submission_count', models.PositiveIntegerField(default=0)),
                ('bot_submission_count', models.PositiveIntegerField(default=0)),
                ('pages_hit', models.JSONField(default=dict)),
            ],
            options={
                'verbose_name': 'IP Record',
                'verbose_name_plural': 'IP Records',
                'ordering': ['-last_seen'],
            },
        ),
    ]
