# Generated by Django 3.1.1 on 2020-12-22 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read', '0005_page_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='no',
        ),
        migrations.AddField(
            model_name='page',
            name='number',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
