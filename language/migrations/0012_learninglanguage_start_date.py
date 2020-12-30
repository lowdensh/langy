# Generated by Django 3.1.1 on 2020-12-30 00:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('language', '0011_auto_20201229_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='learninglanguage',
            name='start_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date started'),
            preserve_default=False,
        ),
    ]