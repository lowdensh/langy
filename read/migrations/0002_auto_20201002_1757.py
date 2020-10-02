# Generated by Django 3.1.1 on 2020-10-02 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='name',
        ),
        migrations.AddField(
            model_name='author',
            name='first_name',
            field=models.CharField(default='bob', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='author',
            name='last_name',
            field=models.CharField(default='bob', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(max_length=50, to='read.Genre'),
        ),
    ]
