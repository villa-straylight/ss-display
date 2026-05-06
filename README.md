# ss-display

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

Configure which sensors to show in `config.ini`, then run:

```bash
python3 ss-display.py
```

Enabled sensors are grouped into pages of 3 (font size 12) or 4 (font size 10) lines and rotate automatically on the configured delay.

### GIF / image display

```bash
python3 oled.py image.gif
```

Supports animated GIFs and static images. Use `none` to blank the screen:

```bash
python3 oled.py none
```

### Profile switching

```bash
python3 profile.py [1-5]
```

## Configuration

All options live in `config.ini`.

### [Appearance]

| Key | Description | Default |
|-----|-------------|---------|
| `Font` | TrueType font file (must be in the same directory) | `SpaceMono-Regular.ttf` |
| `Size` | Font size. 12 fits 3 lines, 10 fits 4 lines | `12` |
| `Delay` | Seconds to show each page before rotating | `2` |
| `GIF` | Path to a GIF or image to display as a rotating page | _(blank)_ |

### [Sensors]

Set any sensor to `True` to enable it. Sensors are displayed in the order listed.

| Key | Description |
|-----|-------------|
| `CpuPercent` | CPU utilisation % |
| `Load1` | 1-minute load average |
| `Load5` | 5-minute load average |
| `Load15` | 15-minute load average |
| `CoreTemp` | CPU core temperature (°C) |
| `GpuTemp` | GPU temperature (°C) |
| `CpuFreq` | Current CPU frequency (MHz) |
| `CpuMax` | Maximum CPU frequency (MHz) |
| `CpuCount` | CPU core count |
| `MemUsed` | Memory used (MiB) |
| `MemFree` | Memory free (MiB) |
| `MemTotal` | Total memory (MiB) |
| `MemUsedPercent` | Memory used % |
| `Swap` | Swap used (MiB) |
| `SwapPercent` | Swap used % |
| `ExternalIP` | External IP address |

## Running as a service

A sample systemd user service is included:

```bash
cp ss-display.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ss-display
```
