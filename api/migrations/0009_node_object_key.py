# Generated by Django 3.2.3 on 2021-06-08 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20210606_0052'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='object_key',
            field=models.CharField(default='nokey', max_length=200),
        ),
    ]