from django.db import models
from django.contrib.auth.models import User

# Hồ sơ cá nhân
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='default.png')

    def __str__(self):
        return f"Hồ sơ của {self.user.username}"
