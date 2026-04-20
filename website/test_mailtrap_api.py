import os
import django
from django.conf import settings
from anymail.message import AnymailMessage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    print("Testing Mailtrap API...")
    msg = AnymailMessage(
        subject="Test Mailtrap API Send",
        body="This is a test from GIS Web using your Anymail API Token.",
        to=["thuanln1907@gmail.com"],
        from_email="hello@demomailtrap.co"
    )
    # Force use of anymail
    msg.send()
    print("Email sent successfully!")
except Exception as e:
    print("Error sending email:", str(e))
