# Generated by Django 4.2.15 on 2024-08-10 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spamapp', '0004_remove_spamreport_count_spam_hits'),
    ]

    operations = [
        migrations.AddField(
            model_name='spamreport',
            name='count_spam_hits',
            field=models.IntegerField(default=0),
        ),
    ]
