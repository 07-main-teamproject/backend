import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
