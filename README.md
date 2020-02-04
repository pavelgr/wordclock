# WORDCLOCK

Just a small side project, e-ink display for a clock (wordclock [!] and other displays), weather (using AccuWeather API), images and reminders, controlled physically and over a Telegram bot.

![as wordclock](/images/k3_clock_words.jpg)
![as analog_clock](/images/k3_clock_hands.jpg)
![as image frame](/images/k3_image.jpg)
![as weather_forecast](/images/k3_weather.jpg)
![as reminder](/images/k3_text.jpg)

Inspired by previous art:
- https://mpetroff.net/2012/09/kindle-weather-display
- https://github.com/pjimenezmateo/kindle-wallpaper
- https://www.instructables.com/id/Literary-Clock-Made-From-E-reader
- https://blog.kylesf.com/my-experience-in-creating-the-worlds-first-low-power-animated-picture-frame-ee24877a4b46

## V1: K3
- Uses a jailbroken Kindle K3 device (800x600, 8bit grayscale, no light, no touchscreen, 2.x kernel, custom rootfs)
- Device part implemented in bash

## V2: Glo HD (in the works)
- Uses a [liberated] Kobo Glo HD device (1448×1072, 16bit grayscale, light, touchscreen, 3.15 kernel, Debian Jessie rootfs)
- Device part implemented in python

