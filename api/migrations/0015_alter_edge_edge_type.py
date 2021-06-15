# Generated by Django 3.2.3 on 2021-06-15 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_article_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edge',
            name='edge_type',
            field=models.CharField(choices=[('coauthor', '0'), ('author_of', '1'), ('topic_of', '2'), ('author_cotopic', '3'), ('article_cotopic', '4')], default='coauthor', max_length=50),
        ),
    ]
