# Generated by Django 4.2.15 on 2024-08-10 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spamapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spamreport',
            name='count_spam_hits',
            field=models.IntegerField(blank=True, max_length=100, null=True),
        ),
    ]
