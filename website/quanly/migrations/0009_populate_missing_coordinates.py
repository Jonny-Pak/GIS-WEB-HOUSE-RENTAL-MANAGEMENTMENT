# Migration để điền tọa độ mặc định cho các nhà chưa có coordinates
from django.db import migrations

# Tọa độ trung tâm của mỗi quận/huyện TP.HCM
DISTRICT_COORDINATES = {
    'q1': (10.7769, 106.7009),      # Quận 1
    'q2': (10.7964, 106.7272),      # Quận 2
    'q3': (10.7931, 106.6788),      # Quận 3
    'q4': (10.7571, 106.6756),      # Quận 4
    'q5': (10.7378, 106.6543),      # Quận 5
    'q6': (10.7611, 106.6362),      # Quận 6
    'q7': (10.7368, 106.7205),      # Quận 7
    'q8': (10.8035, 106.6794),      # Quận 8
    'q9': (10.8364, 106.7479),      # Quận 9
    'q10': (10.7594, 106.6637),     # Quận 10
    'q11': (10.8801, 106.7473),     # Quận 11
    'q12': (10.8945, 106.8162),     # Quận 12
    'qbt': (10.8228, 106.7491),     # Quận Bình Thạnh
    'qtb': (10.8091, 106.6552),     # Quận Tân Bình
    'qtp': (10.8643, 106.6392),     # Quận Tân Phú
    'qp': (10.8068, 106.6946),      # Quận Phú Nhuận
    'qgv': (10.8714, 106.7247),     # Quận Gò Vấp
    'qbtan': (10.7274, 106.6181),   # Quận Bình Tân
    'td': (10.8405, 106.7591),      # Thành phố Thủ Đức
    'hbc': (10.6719, 106.6108),     # Huyện Bình Chánh
    'hhm': (10.6859, 106.7759),     # Huyện Hóc Môn
    'hcc': (10.4517, 106.3857),     # Huyện Củ Chi
    'hnb': (10.6162, 106.7359),     # Huyện Nhà Bè
    'hcg': (10.3581, 106.9836),     # Huyện Cần Giờ
}

def populate_coordinates(apps, schema_editor):
    """Điền tọa độ mặc định cho các nhà không có coordinates"""
    House = apps.get_model('quanly', 'House')
    
    # Lọc những nhà có status là available hoặc rented nhưng thiếu lat hoặc lng
    houses_to_update = House.objects.filter(
        status__in=['available', 'rented']
    ).filter(
        lat__isnull=True
    ) | House.objects.filter(
        status__in=['available', 'rented']
    ).filter(
        lng__isnull=True
    )
    
    updated_count = 0
    for house in houses_to_update:
        if house.district in DISTRICT_COORDINATES:
            lat, lng = DISTRICT_COORDINATES[house.district]
            house.lat = lat
            house.lng = lng
            house.save()
            updated_count += 1
            print(f"Updated: ID {house.id} - {house.name} (lat={lat}, lng={lng})")
    
    print(f"\nTotal updated: {updated_count} houses")

def reverse_coordinates(apps, schema_editor):
    """Rollback: set lat/lng back to None (không thực tế)"""
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('quanly', '0008_migrate_house_status_approved_to_available'),
    ]

    operations = [
        migrations.RunPython(populate_coordinates, reverse_coordinates),
    ]
