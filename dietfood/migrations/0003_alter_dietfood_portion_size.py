# Generated by Django 5.1.6 on 2025-02-14 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dietfood', '0002_dietfood_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dietfood',
            name='portion_size',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=6),
        ),
    ]
