# Generated by Django 4.0.5 on 2022-06-03 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0005_alter_baseletter_cipher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseletter',
            name='subj',
            field=models.TextField(blank=True, null=True, verbose_name='Тема письма'),
        ),
    ]