# Generated by Django 4.1.4 on 2025-01-16 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_alter_ride_card'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rides', to='dashboard.rfidcard'),
        ),
    ]
