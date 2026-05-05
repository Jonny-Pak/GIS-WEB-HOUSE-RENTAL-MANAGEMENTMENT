from django.db import migrations


def backfill_profile_avatar(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    Profile.objects.filter(avatar__in=['', 'default.png', 'avatars/default.png']).update(
        avatar='avatars/avatar.jpg'
    )


def noop_reverse(apps, schema_editor):
    # Keep migrated avatar paths unchanged on reverse to avoid data loss.
    return


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_profile_avatar_default'),
    ]

    operations = [
        migrations.RunPython(backfill_profile_avatar, noop_reverse),
    ]
