# Generated by Django 3.1.1 on 2021-01-21 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('read', '0013_auto_20201228_0134'),
        ('language', '0015_auto_20210120_1935'),
    ]

    operations = [
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foreign_language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='language.foreignlanguage')),
            ],
        ),
        migrations.AlterModelOptions(
            name='translatableword',
            options={},
        ),
        migrations.RemoveField(
            model_name='translatableword',
            name='categories',
        ),
        migrations.AddField(
            model_name='translatableword',
            name='books',
            field=models.ManyToManyField(related_name='translatable_words', to='read.Book'),
        ),
        migrations.DeleteModel(
            name='WordCategory',
        ),
        migrations.AddField(
            model_name='translation',
            name='translatable_word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='language.translatableword'),
        ),
    ]