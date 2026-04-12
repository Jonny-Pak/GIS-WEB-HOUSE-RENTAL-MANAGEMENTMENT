from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

# Hồ sơ cá nhân
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/avatar.jpg')

    def __str__(self):
        return f"Hồ sơ của {self.user.username}"


class EmailOTP(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP {self.code} cho {self.email}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None

    @classmethod
    def generate_unique_code(cls):
        now = timezone.now()
        for _ in range(50):
            candidate = f"{random.randint(0, 999999):06d}"
            exists_active = cls.objects.filter(
                code=candidate,
                used_at__isnull=True,
                expires_at__gt=now,
            ).exists()
            if not exists_active:
                return candidate

        raise RuntimeError('Không thể tạo mã OTP duy nhất, vui lòng thử lại.')
