# Generated by Django 4.0.5 on 2022-06-02 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0002_alter_baseletter_executor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseletter',
            name='executor',
            field=models.ManyToManyField(blank=True, to='letters.executor', verbose_name='Подписано/Исполнитель'),
        ),
    ]