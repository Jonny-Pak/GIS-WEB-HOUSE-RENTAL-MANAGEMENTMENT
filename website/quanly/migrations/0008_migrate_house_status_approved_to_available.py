# Migration để chuyển đổi status 'approved' thành 'available'
from django.db import migrations

def forward_migrate(apps, schema_editor):
    """Chuyển tất cả 'approved' sang 'available'"""
    House = apps.get_model('quanly', 'House')
    House.objects.filter(status='approved').update(status='available')

def reverse_migrate(apps, schema_editor):
    """Rollback: chuyển 'available' từ migration này về 'approved'"""
    # Không làm gì vì không thể phân biệt 'available' cũ vs vừa chuyển
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('quanly', '0007_alter_house_status'),
    ]

    operations = [
        migrations.RunPython(forward_migrate, reverse_migrate),
    ]
