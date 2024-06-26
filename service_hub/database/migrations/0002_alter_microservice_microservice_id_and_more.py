# Generated by Django 4.2 on 2024-06-19 09:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='microservice',
            name='microservice_id',
            field=models.CharField(default=uuid.uuid4, max_length=255),
        ),
        migrations.AlterField(
            model_name='service',
            name='service_id',
            field=models.CharField(default=uuid.uuid4, max_length=255),
        ),
    ]
