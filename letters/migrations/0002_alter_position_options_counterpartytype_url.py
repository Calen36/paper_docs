# Generated by Django 4.0.5 on 2022-06-23 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='position',
            options={'verbose_name': 'должность', 'verbose_name_plural': '    \u2000\u2000\u2000Должности'},
        ),
        migrations.AddField(
            model_name='counterpartytype',
            name='url',
            field=models.CharField(default='avc', max_length=127),
            preserve_default=False,
        ),
    ]