# Generated by Django 5.0.6 on 2024-07-13 15:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0021_singlegamesetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsetting',
            name='daily_playtime',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ArtSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('art_daily_playtime', models.IntegerField(blank=True, null=True)),
                ('art_break_time', models.IntegerField(blank=True, null=True)),
                ('art_break_duration_time', models.IntegerField(blank=True, null=True)),
                ('art_presence_of_ai', models.CharField(choices=[('Always', 'Always'), ('Need', 'Only Appear when child needs')], default='Always', max_length=50)),
                ('child', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='art_setting', to='MyApp.child')),
            ],
        ),
        migrations.CreateModel(
            name='FitnessSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fit_daily_playtime', models.IntegerField(blank=True, null=True)),
                ('fit_break_time', models.IntegerField(blank=True, null=True)),
                ('fit_break_duration_time', models.IntegerField(blank=True, null=True)),
                ('fit_presence_of_ai', models.CharField(choices=[('Always', 'Always'), ('Hurt', 'Appear when child get hurt'), ('Need', 'Only Appear when child needs')], default='Always', max_length=50)),
                ('child', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fitness_setting', to='MyApp.child')),
            ],
        ),
    ]
