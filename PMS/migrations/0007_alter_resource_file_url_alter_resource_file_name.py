# Generated by Django 4.1.7 on 2023-06-13 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PMS', '0006_subtask_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='file_URL',
            field=models.URLField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='file_name',
            field=models.FileField(null=True, upload_to='PMS/file/resources/'),
        ),
    ]
