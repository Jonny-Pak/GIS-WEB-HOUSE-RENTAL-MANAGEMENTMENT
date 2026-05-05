from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseFurnitureItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])),
                ('furniture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='houses.furniture')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='furniture_items', to='houses.house')),
            ],
            options={
                'verbose_name': 'Nội thất theo nhà',
                'verbose_name_plural': 'Nội thất theo nhà',
                'unique_together': {('house', 'furniture')},
            },
        ),
    ]
