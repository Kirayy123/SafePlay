# Generated by Django 5.0.6 on 2024-07-13 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0020_rename_break_duration_time_chatsetting_chat_break_duration_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleGameSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sgame_daily_playtime', models.IntegerField(blank=True, null=True)),
                ('sgame_break_time', models.IntegerField(blank=True, null=True)),
                ('sgame_break_duration_time', models.IntegerField(blank=True, null=True)),
                ('sgame_presence_of_ai', models.CharField(choices=[('Always', 'Always'), ('sometimes', 'Only appear when child needs')], default='Always', max_length=50)),
                ('child', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sgame_setting', to='MyApp.child')),
            ],
        ),
    ]
