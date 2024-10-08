# Generated by Django 5.0.6 on 2024-07-05 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0006_textfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='bully_action',
            field=models.CharField(choices=[('exit', 'BigBuddy verbal reminders for bad behavior AND exclude from the game'), ('notice', 'BigBuddy verbal reminders for bad behavior'), ('ignore', 'No intervention')], default='exit', max_length=50),
        ),
        migrations.AlterField(
            model_name='setting',
            name='victim_action',
            field=models.CharField(choices=[('exit', 'BigBuddy verbal notice about bad behavior AND comfort child'), ('comfort', 'BigBuddy verbal notice about bad behavior'), ('ignore', 'No intervention')], default='exit', max_length=50),
        ),
    ]
