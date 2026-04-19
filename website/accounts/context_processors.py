from django.templatetags.static import static

from .models import Profile
from accounts.models import Notification


def current_user_profile(request):
    """Expose safe avatar data for authenticated users in all templates."""
    if not request.user.is_authenticated:
        return {}

    default_avatar_url = static('images/person_1-min.jpg')
    avatar_url = default_avatar_url
    has_custom_avatar = False

    profile = Profile.objects.filter(user=request.user).only('avatar').first()
    if profile and profile.avatar and getattr(profile.avatar, 'name', ''):
        avatar_name = profile.avatar.name.strip().lower()
        if avatar_name not in {'default.png', 'avatars/default.png'}:
            has_custom_avatar = True
        try:
            avatar_url = profile.avatar.url
        except (ValueError, OSError):
            avatar_url = default_avatar_url

    return {
        'current_user_avatar_url': avatar_url,
        'current_user_has_custom_avatar': has_custom_avatar,
    }


def notification_count(request):
    """Expose notification count for authenticated users in all templates."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        notifications_preview = Notification.objects.filter(user=request.user).order_by('-created_at')[:4]
    else:
        unread_count = 0
        notifications_preview = []
    return {
        'notification_unread_count': unread_count,
        'notification_preview': notifications_preview,
    }
