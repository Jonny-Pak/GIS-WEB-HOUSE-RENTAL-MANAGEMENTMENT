from django.db import migrations, models


def sync_coordinate_status(apps, schema_editor):
    House = apps.get_model('quanly', 'House')
    eligible_statuses = ['pending', 'available', 'no_coordinates']

    # Any record explicitly marked as requiring coordinates becomes no_coordinates.
    House.objects.filter(requires_coordinates=True, status__in=eligible_statuses).update(status='no_coordinates')

    # Any record without lat/lng cannot remain available.
    House.objects.filter(lat__isnull=True, status__in=eligible_statuses).update(requires_coordinates=True)
    House.objects.filter(lng__isnull=True, status__in=eligible_statuses).update(requires_coordinates=True)
    House.objects.filter(requires_coordinates=True, status__in=eligible_statuses).update(status='no_coordinates')


class Migration(migrations.Migration):

    dependencies = [
        ('quanly', '0010_house_requires_coordinates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='status',
            field=models.CharField(
                choices=[
                    ('no_coordinates', 'Chưa có tọa độ'),
                    ('pending', 'Chờ duyệt'),
                    ('available', 'Còn trống'),
                    ('rented', 'Đã cho thuê'),
                    ('hidden', 'Đã ẩn'),
                    ('rejected', 'Bị từ chối'),
                ],
                default='pending',
                max_length=20,
                verbose_name='Trạng thái cho thuê',
            ),
        ),
        migrations.RunPython(sync_coordinate_status, migrations.RunPython.noop),
    ]
