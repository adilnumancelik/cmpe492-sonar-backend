# Generated by Django 3.2.3 on 2021-06-13 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='raw_data',
            field=models.CharField(blank=True, max_length=1000000, null=True),
        ),
    ]