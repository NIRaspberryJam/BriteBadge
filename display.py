import dothat.backlight

try:
    from dothat import backlight
    from dothat import lcd
    DISPLAY = True
except ImportError:
    DISPLAY = False

import netifaces as ni
import datetime

try: # Check if HAT actually attached
    if DISPLAY:
        dothat.backlight.rgb(190, 190, 190)
except:
    DISPLAY = False


def write_ip():
    try:
        ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        display_text(f"IP:{ip}")
    except ValueError:
        display_text("Error - No IP!")


def update_display():
    write_ip()
    display_text(f"Update: {datetime.datetime.now().strftime('%H:%M:%S')}", 0, 1)


def display_text(text, x=0, y=0):
    if DISPLAY:
        lcd.set_cursor_position(x, y)
        lcd.write(text)