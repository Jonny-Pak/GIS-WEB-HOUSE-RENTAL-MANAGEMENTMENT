from django.templatetags.static import static

from .models import Profile


def current_user_profile(request):
    """Expose safe avatar data for authenticated users in all templates."""
    if not request.user.is_authenticated:
        return {}

    default_avatar_url = static('images/avatar.jpg')
    avatar_url = default_avatar_url
    has_custom_avatar = False

    profile = Profile.objects.filter(user=request.user).only('avatar').first()
    if profile and profile.avatar and getattr(profile.avatar, 'name', ''):
        avatar_name = profile.avatar.name.strip().lower()
        if avatar_name in {'default.png', 'avatars/default.png', 'avatar.jpg', 'avatars/avatar.jpg'}:
            has_custom_avatar = False
            avatar_url = default_avatar_url
        else:
            has_custom_avatar = True
            try:
                avatar_url = profile.avatar.url
            except (ValueError, OSError):
                avatar_url = default_avatar_url

    return {
        'current_user_avatar_url': avatar_url,
        'current_user_has_custom_avatar': has_custom_avatar,
    }
