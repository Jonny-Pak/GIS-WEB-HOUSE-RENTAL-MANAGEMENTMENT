# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quanly', '0009_populate_missing_coordinates'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='requires_coordinates',
            field=models.BooleanField(default=False, verbose_name='Chần nhập tọa độ'),
        ),
    ]
