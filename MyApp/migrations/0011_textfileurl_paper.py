# Generated by Django 5.0.6 on 2024-07-06 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0010_textfileurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='textfileurl',
            name='paper',
            field=models.CharField(default=2, max_length=200),
            preserve_default=False,
        ),
    ]
