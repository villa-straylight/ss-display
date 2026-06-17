# ss-display

![W.gif](W.gif)

A Python utility for displaying system stats and GIF animations on the OLED screen of supported SteelSeries keyboards. Forked from [steelseries-oled](https://github.com/edbgon/steelseries-oled).

## Supported Devices

- Apex 7
- Apex 7 TKL
- Apex Pro
- Apex 5

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### System stats display

Configure which sensors to show in `config.yaml`, then run:

```bash
python3 ss-display.py
```

Enabled sensors are grouped into pages of 3 (font size 12) or 4 (font size 10) lines and rotate automatically on the configured delay. An image or GIF can also be added as a rotating page — `W.gif` is included as an example.

## Configuration

All options live in `config.yaml`.

### appearance

| Key | Description | Default |
|-----|-------------|---------|
| `font` | TrueType font file (must be in the same directory) | `SpaceMono-Regular.ttf` |
| `size` | Font size. 12 fits 3 lines, 10 fits 4 lines | `12` |
| `delay` | Seconds to show each page before rotating | `2` |
| `image` | Path to an image or GIF to display as a rotating page (PNG, JPEG, GIF, etc.) | _(blank)_ |

### sensors

Set any sensor to `true` to enable it. Sensors are displayed in the order listed.

| Key | Description |
|-----|-------------|
| `cpu_percent` | CPU utilisation % |
| `load1` | 1-minute load average |
| `load5` | 5-minute load average |
| `load15` | 15-minute load average |
| `core_temp` | CPU core temperature (°C) |
| `gpu_temp` | GPU temperature (°C) |
| `cpu_freq` | Current CPU frequency (MHz) |
| `cpu_max` | Maximum CPU frequency (MHz) |
| `cpu_count` | CPU core count |
| `mem_used` | Memory used (MiB) |
| `mem_free` | Memory free (MiB) |
| `mem_total` | Total memory (MiB) |
| `mem_used_percent` | Memory used % |
| `swap` | Swap used (MiB) |
| `swap_percent` | Swap used % |
| `battery` | Battery level and charge state (e.g. `85%+`) |
| `disk_usage` | Usage % for each local mounted filesystem (ext2/3/4, btrfs, xfs, zfs, ntfs, etc.) |
| `fan_speeds` | RPM for all available fans |
| `external_ip` | External IP address |

## Hardware compatibility

### CPU temperature

Auto-detected for Intel (`coretemp`), AMD via `k10temp` (prefers `Tdie` over `Tctl` to avoid the +27°C offset on early Ryzen), and AMD via the `zenpower` driver.

### GPU temperature

| GPU | Status |
|-----|--------|
| NVIDIA | Tested — via GPUtil |
| Intel Xe / Arc | Tested — via `xe` sensor |
| AMD | Untested — implemented based on documented `amdgpu` sensor labels |

AMD GPU support has not been tested against real hardware. If `gpu_temp` shows nothing or wrong values on your AMD GPU, please open an issue and include the output of:

```bash
python3 -c "import psutil; [print(k, [(e.label, e.current) for e in v]) for k,v in psutil.sensors_temperatures().items()]"
```

## Running as a service

A sample systemd user service is included. Update `WorkingDirectory` to match your install path:

```bash
cp ss-display.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ss-display
```

## Autostart / app launcher

A sample `.desktop` file is included. Update the `Exec` path to match your install location, then copy it to the appropriate directory:

```bash
# autostart on login
cp ss-display.desktop ~/.config/autostart/

# or add to the app launcher
cp ss-display.desktop ~/.local/share/applications/
```

## Changelog

### 2026-06-17

#### Changed
- Screen rotation delay increased from 2s to 5s
- Fan sensors now skip headers with no fan attached (RPM == 0) at startup

---

### 2026-05-06

#### Security
- External IP lookup switched from HTTP to HTTPS (`api.ipify.org`) to prevent MITM on untrusted networks
- Added 5-second timeout to external IP request so a slow or unreachable server can't freeze the display

#### Added
- CPU temperature auto-detection for AMD systems: `k10temp` driver (prefers `Tdie` over `Tctl` to avoid the +27°C offset on early Ryzen) and `zenpower` driver
- GPU temperature support for AMD (`amdgpu` sensor, `edge`/`junction` labels) and Intel Xe/Arc (`xe` sensor, `pkg` label), alongside existing NVIDIA support via GPUtil

#### Changed
- Config format converted from INI (`config.ini`) to YAML (`config.yaml`); sensor keys are now `snake_case`
- Sensor polling optimized: related psutil calls cached per tick to avoid redundant syscalls when multiple sensors share the same data source
- External IP result cached for 5 minutes (was fetched every tick)

#### Fixed
- `core_temp` no longer crashes on AMD systems
- `cpu_freq` and `cpu_max` no longer crash on systems where `psutil.cpu_freq()` returns `None`
- Disk usage sensor guards against filesystems unmounted after startup
- Config lookups hardened against blank YAML values

---

### 2026-05-05

#### Added
- Disk usage, battery, and fan speed sensors
- Image and GIF support as a rotating display page
- Config-driven sensor selection
- Sample systemd user service unit and `.desktop` file
- `requirements.txt`

#### Changed
- Refactored into `ss-display.py` + `functions.py`
- Paths use `realpath`-anchored resolution instead of `chdir`

---

### Upstream (forked from [steelseries-oled](https://github.com/edbgon/steelseries-oled))

- Apex Pro and Apex 7 TKL support
- SIGTERM handling
- Static image display and screen blanking
