from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0007_iprecord_enrichment'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsubmission',
            name='ip_record',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='contact_submissions',
                to='upload.iprecord',
            ),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='ip_record',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='page_visits',
                to='upload.iprecord',
            ),
        ),
        migrations.AddField(
            model_name='telegrammessage',
            name='sender',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='messages',
                to='upload.telegramuser',
                to_field='user_id',
            ),
        ),
    ]
