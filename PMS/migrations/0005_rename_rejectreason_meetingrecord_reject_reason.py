# Generated by Django 4.1.7 on 2023-06-07 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PMS', '0004_supervisorprofile_email_supervisorprofile_first_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meetingrecord',
            old_name='rejectReason',
            new_name='reject_reason',
        ),
    ]
