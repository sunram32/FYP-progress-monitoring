# Generated by Django 4.1.7 on 2023-06-13 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PMS', '0007_alter_resource_file_url_alter_resource_file_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='PMS.task'),
        ),
    ]