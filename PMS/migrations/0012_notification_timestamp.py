# Generated by Django 4.1.7 on 2023-06-15 07:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PMS', '0011_alter_notification_chat_resource_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 15, 15, 5, 36, 928022)),
        ),
    ]
