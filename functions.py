#!/usr/bin/env python3
import configparser
import re
from easyhid import Enumeration
from urllib.request import urlopen
from PIL import Image, ImageSequence
import psutil
import GPUtil

def init_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def getdevice():
    # Stores an enumeration of all the connected USB HID devices
    en = Enumeration()

    #List of known working devices, add your PID here if it works
    #                Apex 7,  7 TKL, Pro     Apex 5
    supported_pid = (0x1612, 0x1618, 0x1610, 0x161c)

    # Return a list of devices based on the search parameters
    devices = en.find(vid=0x1038, interface=1)
    if not devices:
        exit("No SteelSeries devices found, exiting.")
    # Need to figure out how to handle multiple devices gracefully
    # for now we pick the first one that shows up
    for device in devices:
        if device.product_id in supported_pid:
            return device

    exit("No compatible SteelSeries devices found, exiting.")

def load1():
    return round(psutil.getloadavg()[0], 3)

def load5():
    return round(psutil.getloadavg()[1], 3)

def load15():
    return round(psutil.getloadavg()[2], 3)

def core_temp():
    return psutil.sensors_temperatures()['coretemp'][0].current

def gpu_temp():
    try:
        return GPUtil.getGPUs()[0].temperature
    except:
        return None

def swap_use():
    return round(psutil.swap_memory()[1]/1048576)

def swap_percent():
    return psutil.swap_memory()[3]

def mem_free():
    return round(psutil.virtual_memory()[1]/1048576)

def mem_used():
    return round(psutil.virtual_memory()[3]/1048576)

def mem_used_percent():
    return psutil.virtual_memory()[2]

def mem_total():
    return round(psutil.virtual_memory()[0]/1048576)

def cpu_percent():
    return psutil.cpu_percent(interval=1)

def cpu_freq():
    return psutil.cpu_freq()[0]

def cpu_max():
    return psutil.cpu_freq().max

def cpu_count():
    return psutil.cpu_count()

def ext_ip():
    d = str(urlopen('http://checkip.dyndns.com/').read())
    return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(d).group(1)

def load_gif(path):
    im = Image.open(path)
    frames = []
    last_frame = None
    for frame in ImageSequence.Iterator(im):
        last_frame = frame
        frame = frame.resize((128, 40)).convert('1')
        frames.append(bytearray([0x61]) + frame.tobytes() + bytearray([0x00]))
    sleeptime = last_frame.info.get('duration', 1000) / 1000
    return frames, sleeptime

def draw_init(draw):
    draw.rectangle([(0,0),(128,40)], fill=0)

def draw_text_3(draw, font, stat_one, stat_two, stat_three):
    draw.text((1,  1), stat_one,   font=font, fill=255)
    draw.text((1, 11), stat_two,   font=font, fill=255)
    draw.text((1, 21), stat_three, font=font, fill=255)

def draw_text_4(draw, font, stat_one, stat_two, stat_three, stat_four):
    draw.text((1,  1), stat_one,   font=font, fill=255)
    draw.text((1, 11), stat_two,   font=font, fill=255)
    draw.text((1, 21), stat_three, font=font, fill=255)
    draw.text((1, 31), stat_four,  font=font, fill=255)

        
