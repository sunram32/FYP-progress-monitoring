# Generated by Django 4.1.7 on 2023-06-12 06:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('PMS', '0005_rename_rejectreason_meetingrecord_reject_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='due_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
