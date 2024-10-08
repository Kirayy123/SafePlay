# Generated by Django 5.0.6 on 2024-07-06 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0011_textfileurl_paper'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='game_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.IntegerField(choices=[(0, 'Enter game'), (3, 'Exit game'), (1, 'Bullying victim'), (2, 'Bully')], default=0),
        ),
    ]
