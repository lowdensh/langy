# Generated by Django 3.1.1 on 2020-10-02 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read', '0004_auto_20201002_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(default='default', max_length=50),
            preserve_default=False,
        ),
    ]
