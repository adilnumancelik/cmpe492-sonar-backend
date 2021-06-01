# Generated by Django 3.2.3 on 2021-06-01 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_article_articlelist_articlelisttodoi_edge_node'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=256)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('register_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='articlelist',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='articlelisttodoi',
            name='article_list_id',
        ),
        migrations.RemoveField(
            model_name='edge',
            name='article_list_id',
        ),
        migrations.RemoveField(
            model_name='node',
            name='article_list_id',
        ),
        migrations.AddField(
            model_name='articlelisttodoi',
            name='article_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.articlelist'),
        ),
        migrations.AddField(
            model_name='edge',
            name='article_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.articlelist'),
        ),
        migrations.AddField(
            model_name='node',
            name='article_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.articlelist'),
        ),
        migrations.AddField(
            model_name='articlelist',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.user'),
        ),
    ]
