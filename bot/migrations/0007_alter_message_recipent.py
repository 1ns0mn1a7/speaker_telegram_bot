# Generated by Django 5.2 on 2025-05-22 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_message_header_alter_message_creation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='recipent',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='messages', to='bot.participant', verbose_name='Кому отправлено'),
        ),
    ]
