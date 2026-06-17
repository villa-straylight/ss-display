#!/usr/bin/env python3
import os
import yaml
from time import monotonic
from easyhid import Enumeration
from urllib.request import urlopen
from PIL import Image, ImageSequence
import psutil


# Cache wrapper: calls the wrapped function at most once per `ttl` seconds.
# Used below so that related sensors (e.g. load1/load5/load15) share a single
# syscall per display tick rather than each making their own.
def _ttl_cache(ttl):
    def decorator(fn):
        result = [None]
        expires = [0.0]
        def wrapper():
            now = monotonic()
            if now >= expires[0]:
                result[0] = fn()
                expires[0] = now + ttl
            return result[0]
        return wrapper
    return decorator


# Cached psutil calls — multiple sensor functions read from the same underlying
# data source, so we fetch it once per tick (0.5s window) instead of once per sensor.
_getloadavg          = _ttl_cache(0.5)(psutil.getloadavg)
_swap_memory         = _ttl_cache(0.5)(psutil.swap_memory)
_virtual_memory      = _ttl_cache(0.5)(psutil.virtual_memory)
_sensors_fans_all    = _ttl_cache(0.5)(psutil.sensors_fans)
_sensors_temps_all   = _ttl_cache(0.5)(psutil.sensors_temperatures)

def init_config(path='config.yaml'):
    with open(path) as f:
        return yaml.safe_load(f)

def getdevice(device_config=None):
    cfg = device_config or {}
    en = Enumeration()

    # Manual override: if vid+pid are both specified, find that exact device
    if cfg.get('vid') and cfg.get('pid'):
        vid = int(cfg['vid'])
        pid = int(cfg['pid'])
        interface = int(cfg.get('interface', 1))
        devices = en.find(vid=vid, pid=pid, interface=interface)
        if not devices:
            exit("No HID device found with VID=0x{:04x} PID=0x{:04x}, exiting.".format(vid, pid))
        return devices[0]

    # SteelSeries auto-detection
    #                Apex 7,  7 TKL, Pro     Apex 5
    supported_pid = (0x1612, 0x1618, 0x1610, 0x161c)
    devices = en.find(vid=0x1038, interface=1)
    if not devices:
        exit("No SteelSeries devices found, exiting.")
    for device in devices:
        if device.product_id in supported_pid:
            return device

    exit("No compatible SteelSeries devices found, exiting.")

def load1():
    return round(_getloadavg()[0], 3)

def load5():
    return round(_getloadavg()[1], 3)

def load15():
    return round(_getloadavg()[2], 3)

def _pick_temp(entries, *preferred_labels):
    for label in preferred_labels:
        match = next((e for e in entries if e.label == label), None)
        if match:
            return match.current
    return entries[0].current if entries else None

def core_temp():
    try:
        temps = _sensors_temps_all()
    except Exception:
        return None

    # Intel
    if temps.get('coretemp'):
        return temps['coretemp'][0].current

    # AMD (k10temp driver) — prefer Tdie (no offset) over Tctl (+27°C on early Ryzen)
    if temps.get('k10temp'):
        return _pick_temp(temps['k10temp'], 'Tdie', 'Tctl')

    # AMD (zenpower driver, alternative to k10temp)
    if temps.get('zenpower'):
        return _pick_temp(temps['zenpower'], 'TDIE')

    return None

def gpu_temp():
    # NVIDIA — lazy import so distutils removal in Python 3.14+ doesn't break startup
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].temperature
    except Exception:
        pass

    try:
        temps = _sensors_temps_all()
    except Exception:
        return None

    # AMD GPU — edge is die temp, junction is hotspot
    if temps.get('amdgpu'):
        return _pick_temp(temps['amdgpu'], 'edge', 'junction')

    # Intel Xe / Arc
    if temps.get('xe'):
        return _pick_temp(temps['xe'], 'pkg')

    return None

def swap_use():
    return round(_swap_memory()[1]/1048576)

def swap_percent():
    return _swap_memory()[3]

def mem_free():
    return round(_virtual_memory()[1]/1048576)

def mem_used():
    return round(_virtual_memory()[3]/1048576)

def mem_used_percent():
    return _virtual_memory()[2]

def mem_total():
    return round(_virtual_memory()[0]/1048576)

def cpu_percent():
    return psutil.cpu_percent(interval=1)

def cpu_freq():
    # /proc/cpuinfo reflects the actual current frequency including turbo/throttle;
    # psutil.cpu_freq() returns a cached or nominal value on some kernels.
    with open('/proc/cpuinfo') as f:
        for line in f:
            if line.startswith('cpu MHz'):
                return float(line.split(':')[1].strip())
    freq = psutil.cpu_freq()
    return freq[0] if freq else None

def cpu_max():
    freq = psutil.cpu_freq()
    return freq.max if freq else None

def cpu_count():
    return psutil.cpu_count()

@_ttl_cache(300)
def ext_ip():
    try:
        return urlopen('https://api.ipify.org', timeout=5).read().decode().strip()
    except Exception:
        return None

def battery():
    b = psutil.sensors_battery()
    if b is None:
        return None
    return "{:.0f}%{}".format(b.percent, "+" if b.power_plugged else "-")

_LOCAL_FSTYPES = {
    'ext2', 'ext3', 'ext4', 'btrfs', 'xfs', 'zfs',
    'ntfs', 'exfat', 'f2fs', 'apfs', 'reiserfs', 'jfs',
}

def get_local_disk_sensors():
    sensors = []
    for part in psutil.disk_partitions(all=False):
        if part.fstype not in _LOCAL_FSTYPES:
            continue
        mount = part.mountpoint
        label = os.path.basename(mount) or '/'
        fmt = "{}: {{:.0f}}%".format(label)
        # m=mount captures the current value of mount; without it, all lambdas
        # would close over the same variable and return data for the last mount only.
        fn = lambda m=mount: psutil.disk_usage(m).percent if os.path.ismount(m) else None
        sensors.append((fmt, fn))
    return sensors

def get_fan_sensors():
    def make_fn(name, idx):
        def fn():
            entries = _sensors_fans_all().get(name, [])
            return entries[idx].current if idx < len(entries) else None
        return fn

    sensors = []
    fans = psutil.sensors_fans()
    if not fans:
        return sensors
    for name, entries in fans.items():
        for i, fan in enumerate(entries):
            if fan.current == 0:
                continue
            label = name if len(entries) == 1 else "{} {}".format(name, i + 1)
            fmt = "{}: {{}}rpm".format(label[:10])
            sensors.append((fmt, make_fn(name, i)))
    return sensors

def load_image(path, width=128, height=40, report_id=0x61):
    im = Image.open(path)
    frames = []
    last_frame = None
    for frame in ImageSequence.Iterator(im):
        last_frame = frame
        frame = frame.resize((width, height)).convert('1')
        frames.append(bytearray([report_id]) + frame.tobytes() + bytearray([0x00]))
    sleeptime = last_frame.info.get('duration', 1000) / 1000
    return frames, sleeptime

def draw_init(draw, width=128, height=40):
    draw.rectangle([(0, 0), (width, height)], fill=0)

def draw_text_3(draw, font, stat_one, stat_two, stat_three):
    draw.text((1,  1), stat_one,   font=font, fill=255)
    draw.text((1, 11), stat_two,   font=font, fill=255)
    draw.text((1, 21), stat_three, font=font, fill=255)

def draw_text_4(draw, font, stat_one, stat_two, stat_three, stat_four):
    draw.text((1,  1), stat_one,   font=font, fill=255)
    draw.text((1, 11), stat_two,   font=font, fill=255)
    draw.text((1, 21), stat_three, font=font, fill=255)
    draw.text((1, 31), stat_four,  font=font, fill=255)

        
