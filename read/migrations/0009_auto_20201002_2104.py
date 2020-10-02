# Generated by Django 3.1.1 on 2020-10-02 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read', '0008_auto_20201002_2057'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='translatableword',
            options={'ordering': ['english_word']},
        ),
        migrations.RemoveField(
            model_name='category',
            name='words',
        ),
        migrations.AddField(
            model_name='translatableword',
            name='categories',
            field=models.ManyToManyField(to='read.Category'),
        ),
    ]