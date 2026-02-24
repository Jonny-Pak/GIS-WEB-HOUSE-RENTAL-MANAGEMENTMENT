from rest_framework import serializers
from .models import House

class HouseSerializer(serializers.ModelSerializer):
    district = serializers.CharField(source='get_district_display', read_only=True)
    image = serializers.SerializerMethodField()
    coords = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = House
        fields = ['id', 'name', 'price', 'address', 'district', 'image', 'coords', 'distance']

    def get_image(self, obj):
        if obj.main_image:
            return obj.main_image.url
        return "/static/images/default.jpg"

    def get_coords(self, obj):
        if obj.lat is not None and obj.lng is not None:
            return {"lat": obj.lat, "lng": obj.lng}
        return None

    def get_distance(self, obj):
        if hasattr(obj, 'distance') and obj.distance is not None:
            return round(obj.distance, 2)
        return None
