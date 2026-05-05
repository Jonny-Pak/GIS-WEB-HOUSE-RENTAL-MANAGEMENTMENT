import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    print("Attempting to send test email...")
    send_mail(
        'Test OTP',
        'Your test OTP is 123456',
        settings.DEFAULT_FROM_EMAIL,
        ['tkhoa1933@gmail.com'], # Sending to a known email
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
