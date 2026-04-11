from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0002_telegramuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('company', models.CharField(blank=True, max_length=255)),
                ('service', models.CharField(blank=True, max_length=255)),
                ('message', models.TextField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Contact Submission',
                'verbose_name_plural': 'Contact Submissions',
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.CreateModel(
            name='PageVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=500)),
                ('referrer', models.CharField(blank=True, max_length=2000)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('visited_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Page Visit',
                'verbose_name_plural': 'Page Visits',
                'ordering': ['-visited_at'],
            },
        ),
    ]
