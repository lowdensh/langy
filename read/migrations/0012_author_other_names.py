# Generated by Django 3.1.1 on 2020-10-03 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('read', '0011_remove_book_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='other_names',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]