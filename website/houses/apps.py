import os
from django.apps import AppConfig


class HousesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'houses'

    def ready(self):
        """Tự động tạo các thư mục con cần thiết trong MEDIA_ROOT khi server khởi động."""
        try:
            from django.conf import settings
            media_subdirs = ['house', 'house_images', 'avatars']
            for sub in media_subdirs:
                path = os.path.join(settings.MEDIA_ROOT, sub)
                os.makedirs(path, exist_ok=True)
        except Exception:
            pass  # Bỏ qua nếu settings chưa sẵn sàng (ví dụ khi chạy test)
