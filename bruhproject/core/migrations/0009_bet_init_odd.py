# Generated by Django 3.1.8 on 2021-06-15 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20210521_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet',
            name='init_odd',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
