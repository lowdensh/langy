# Generated by Django 3.1.1 on 2020-11-11 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_foreignlanguage_learninglanguage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ForeignLanguage',
            new_name='uForeignLanguage',
        ),
    ]
