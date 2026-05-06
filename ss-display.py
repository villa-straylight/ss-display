#!/usr/bin/env python3

from PIL import Image, ImageFont, ImageDraw
from time import sleep, monotonic
import os
import signal
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

from functions import (
    init_config, getdevice,
    cpu_percent, cpu_freq, cpu_max, cpu_count,
    core_temp, gpu_temp,
    load1, load5, load15,
    mem_used, mem_free, mem_total, mem_used_percent,
    swap_use, swap_percent,
    ext_ip,
    battery,
    get_local_disk_sensors, get_fan_sensors,
    load_image,
    draw_init, draw_text_3, draw_text_4,
)

config = init_config(os.path.join(SCRIPT_DIR, 'config.yaml'))
appearance = config.get('appearance') or {}
sensors = config.get('sensors') or {}

font_file = os.path.join(SCRIPT_DIR, appearance.get('font') or 'SpaceMono-Regular.ttf')
font_size = appearance.get('size') or 12
delay = appearance.get('delay') or 2
lines_per_page = 3 if font_size >= 12 else 4
draw_fn = draw_text_3 if lines_per_page == 3 else draw_text_4

SENSOR_MAP = [
    ('cpu_percent',      'CPU: {:.0f}%',         cpu_percent),
    ('load1',            'Load1: {}',             load1),
    ('load5',            'Load5: {}',             load5),
    ('load15',           'Load15: {}',            load15),
    ('core_temp',        'CPU temp: {}C',         core_temp),
    ('gpu_temp',         'GPU temp: {}C',         gpu_temp),
    ('cpu_freq',         'CPU Freq: {:.0f}MHz',   cpu_freq),
    ('cpu_max',          'CPU Max: {:.0f}MHz',    cpu_max),
    ('cpu_count',        'CPU cores: {}',         cpu_count),
    ('mem_used',         'Mem: {}MiB',            mem_used),
    ('mem_free',         'MemFree: {}MiB',        mem_free),
    ('mem_total',        'MemTotal: {}MiB',       mem_total),
    ('mem_used_percent', 'Mem: {}%',              mem_used_percent),
    ('swap',             'Swap: {}MiB',           swap_use),
    ('swap_percent',     'Swap: {}%',             swap_percent),
    ('battery',          'Bat: {}',               battery),
    ('external_ip',      'IP: {}',                ext_ip),
]

enabled = [
    (fmt, fn)
    for key, fmt, fn in SENSOR_MAP
    if sensors.get(key, False)
]

if sensors.get('disk_usage', False):
    enabled.extend(get_local_disk_sensors())

if sensors.get('fan_speeds', False):
    enabled.extend(get_fan_sensors())

image_frames = []
image_sleeptime = 0
image_path = (appearance.get('image') or '').strip()
if image_path:
    image_path = os.path.join(SCRIPT_DIR, image_path)
    try:
        image_frames, image_sleeptime = load_image(image_path)
    except Exception as e:
        print("Could not load image: {}".format(e))

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

# HID feature report format: 1 byte report ID (0x61) + 640 bytes of pixel data
# (128×40 pixels at 1 bit each = 640 bytes) + 1 byte terminator = 642 bytes total.
def send_frame():
    dev.send_feature_report(bytearray([0x61]) + im.tobytes() + bytearray([0x00]))

def blank():
    dev.send_feature_report(bytearray([0x61] + [0x00] * 641))

pages = [enabled[i:i + lines_per_page] for i in range(0, len(enabled), lines_per_page)]

while True:
    if not enabled and not image_frames:
        sleep(delay)
        continue

    for page in pages:
        draw_init(draw)
        lines = []
        for fmt, fn in page:
            val = fn()
            lines.append(fmt.format(val) if val is not None else "")
        while len(lines) < lines_per_page:
            lines.append("")
        draw_fn(draw, font, *lines)
        send_frame()
        sleep(delay)
        blank()
        sleep(0.05)  # brief pause to let the HID report complete before the next send

    if image_frames:
        end = monotonic() + delay
        idx = 0
        while monotonic() < end:
            dev.send_feature_report(image_frames[idx % len(image_frames)])
            sleep(image_sleeptime)
            idx += 1
        blank()
        sleep(0.05)  # brief pause to let the HID report complete before the next send

dev.close()
