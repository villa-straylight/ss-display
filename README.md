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

Configure which sensors to show in `config.ini`, then run:

```bash
python3 ss-display.py
```

Enabled sensors are grouped into pages of 3 (font size 12) or 4 (font size 10) lines and rotate automatically on the configured delay. An image or GIF can also be added as a rotating page — `W.gif` is included as an example.

## Configuration

All options live in `config.ini`.

### [Appearance]

| Key | Description | Default |
|-----|-------------|---------|
| `Font` | TrueType font file (must be in the same directory) | `SpaceMono-Regular.ttf` |
| `Size` | Font size. 12 fits 3 lines, 10 fits 4 lines | `12` |
| `Delay` | Seconds to show each page before rotating | `2` |
| `Image` | Path to an image or GIF to display as a rotating page (PNG, JPEG, GIF, etc.) | _(blank)_ |

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
| `Battery` | Battery level and charge state (e.g. `85%+`) |
| `DiskUsage` | Usage % for each local mounted filesystem (ext2/3/4, btrfs, xfs, zfs, ntfs, etc.) |
| `FanSpeeds` | RPM for all available fans |
| `ExternalIP` | External IP address |

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
