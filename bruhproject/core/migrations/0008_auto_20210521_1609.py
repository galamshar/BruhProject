# Generated by Django 3.1.8 on 2021-05-21 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20210521_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='settled',
            field=models.BooleanField(default=False),
        ),
    ]
