# Generated by Django 3.2.3 on 2021-06-01 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210601_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='other_stuff',
            field=models.CharField(blank=True, max_length=10000),
        ),
        migrations.AlterField(
            model_name='article',
            name='raw_data',
            field=models.CharField(blank=True, max_length=10000),
        ),
    ]
