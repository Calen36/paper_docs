# Generated by Django 4.0.5 on 2022-06-28 21:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0002_alter_position_options_counterpartytype_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutgoingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'verbose_name': 'Тип исходящего письма',
                'verbose_name_plural': 'Типы исходящих писем',
            },
        ),
        migrations.AlterModelOptions(
            name='outecoletter',
            options={'verbose_name': 'Исходящее письмо', 'verbose_name_plural': '       \u2000\u2000\u2000📨 Исходящие'},
        ),
        migrations.AlterModelOptions(
            name='position',
            options={'verbose_name': 'должность', 'verbose_name_plural': '    \u2000\u2000\u2000💼 Должности'},
        ),
        migrations.AlterField(
            model_name='counterparty',
            name='name',
            field=models.CharField(max_length=255, verbose_name=''),
        ),
        migrations.AddField(
            model_name='baseletter',
            name='out_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='letters.outgoingtype'),
        ),
    ]
