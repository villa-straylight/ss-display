# Changelog

## 2026-06-17

### Added
- Device config overrides (`vid`, `pid`, `interface`, `report_id`, `width`, `height`) under a `device:` section in `config.yaml` to support non-SteelSeries OLED keyboards; SteelSeries auto-detection is unchanged when these are omitted

### Changed
- Screen rotation delay increased from 2s to 5s
- Fan sensors now skip headers with no fan attached (RPM == 0) at startup

---

## 2026-05-06

### Security
- External IP lookup switched from HTTP to HTTPS (`api.ipify.org`) to prevent MITM on untrusted networks
- Added 5-second timeout to external IP request so a slow or unreachable server can't freeze the display

### Added
- CPU temperature auto-detection for AMD systems: `k10temp` driver (prefers `Tdie` over `Tctl` to avoid the +27°C offset on early Ryzen) and `zenpower` driver
- GPU temperature support for AMD (`amdgpu` sensor, `edge`/`junction` labels) and Intel Xe/Arc (`xe` sensor, `pkg` label), alongside existing NVIDIA support via GPUtil

### Changed
- Config format converted from INI (`config.ini`) to YAML (`config.yaml`); sensor keys are now `snake_case`
- Sensor polling optimized: related psutil calls (`getloadavg`, `swap_memory`, `virtual_memory`, `sensors_temperatures`, `sensors_fans`) are now cached per tick to avoid redundant syscalls when multiple sensors share the same data source
- External IP result cached for 5 minutes (was fetched every tick)
- Page list pre-computed at startup instead of every loop iteration

### Fixed
- `core_temp` no longer crashes on AMD systems (`KeyError` on missing `coretemp` key)
- `cpu_freq` and `cpu_max` no longer crash on systems where `psutil.cpu_freq()` returns `None`
- `gpu_temp` error handling tightened from bare `except` to `except Exception`
- Disk usage sensor guards against filesystems unmounted after startup
- All config lookups hardened against blank YAML values returning `None` instead of a string
- `signal_handler` bare `except` replaced with `except Exception`

### Removed
- `config.ini` (replaced by `config.yaml`)
- Unused `re` import (no longer needed after simplifying external IP response parsing)

---

## 2026-05-05

### Added
- Disk usage sensor (per local mounted filesystem)
- Battery sensor (level and charge state)
- Fan speed sensors (all available fans, in RPM)
- Image and GIF support as a rotating display page
- Config-driven sensor selection
- Sample systemd user service unit (`ss-display.service`)
- Sample `.desktop` file for autostart and app launchers
- `requirements.txt`

### Changed
- Refactored into `ss-display.py` + `functions.py`
- Paths use `realpath`-anchored resolution instead of `chdir`
- Image/GIF feature renamed from GIF-only to reflect support for PNG, JPEG, and other formats

### Removed
- `oled.py`, `profile.py`, `sysstats.py` (unused scripts from upstream fork)

---

## Upstream (forked from [steelseries-oled](https://github.com/edbgon/steelseries-oled))

### Added
- Apex Pro support
- Apex 7 TKL support
- SIGTERM handling
- Static image display support
- Screen blanking between updates

### Changed
- Device detection switched to explicit PID allowlist
- Code restructured and imports optimized
