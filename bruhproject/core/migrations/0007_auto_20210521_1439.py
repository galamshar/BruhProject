# Generated by Django 3.1.8 on 2021-05-21 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20210521_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bet',
            name='settled',
            field=models.BooleanField(null=True),
        ),
    ]
