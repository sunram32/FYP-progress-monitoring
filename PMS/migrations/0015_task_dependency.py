# Generated by Django 4.1.7 on 2023-06-16 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PMS', '0014_task_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='dependency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='PMS.task'),
        ),
    ]