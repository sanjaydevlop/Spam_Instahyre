# Generated by Django 4.2.15 on 2024-08-10 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spamapp', '0003_remove_spamreport_reported_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spamreport',
            name='count_spam_hits',
        ),
    ]
