import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login('tle19072005@gmail.com', 'tiutqvgiwpacegqc')
    print("Login successful!")
    server.quit()
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
