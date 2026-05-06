#!/usr/bin/env python3

from PIL import Image, ImageFont, ImageDraw
from time import sleep
import signal
import sys
import psutil

from functions import (
    init_config, getdevice,
    core_temp, load1, cpu_freq, cpu_count,
    mem_used, swap_use,
    draw_init, draw_text_3,
)

config = init_config()
font_file = config.get('Appearance', 'Font', fallback='SpaceMono-Regular.ttf').strip('"')
font_size = config.getint('Appearance', 'Size', fallback=12)
delay = config.getfloat('Appearance', 'Delay', fallback=2)

dev = getdevice()

def signal_handler(sig, frame):
    try:
        dev.send_feature_report(bytearray([0x61] + [0x00] * 641))
        dev.close()
        print("\n")
        sys.exit(0)
    except:
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if sys.stdout.isatty():
    print("Press Ctrl-C to exit.\n")

dev.open()

im = Image.new('1', (128, 40))
draw = ImageDraw.Draw(im)
font = ImageFont.truetype(font_file, font_size)

while True:
    # Screen 1: CPU stats
    draw_init(draw)
    draw_text_3(
        draw, font,
        "CPU: {:2.0f}%, {:2d} cores".format(psutil.cpu_percent(interval=1), cpu_count()),
        "CPU temp: {0}C".format(core_temp()),
        "Load: {0}".format(load1()),
    )
    dev.send_feature_report(bytearray([0x61]) + im.tobytes() + bytearray([0x00]))
    sleep(delay)

    # Screen 2: Memory stats
    dev.send_feature_report(bytearray([0x61] + [0x00] * 641))
    sleep(0.05)
    draw_init(draw)
    draw_text_3(
        draw, font,
        "CPU Freq: {:4.0f}MHz".format(cpu_freq()),
        "Memory: {0}MiB".format(mem_used()),
        "Swap: {0}MiB".format(swap_use()),
    )
    dev.send_feature_report(bytearray([0x61]) + im.tobytes() + bytearray([0x00]))
    sleep(delay)

dev.close()
