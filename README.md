# ♨️ Acond Heat Pump for Home Assistant

Home Assistant integration for **Acond Therm** heat pumps over **Modbus TCP** — a native integration installable from HACS (config flow, no YAML, no extra Python dependencies) — plus an illustrated Lovelace dashboard that shows the whole system (outdoor unit, flow/return pipes, house heating circuit, DHW tank) with live values and lets you control it.

🌐 **[Česká verze README](README.cs.md)**

![Platform](https://img.shields.io/badge/platform-Home%20Assistant-41BDF5)
![Protocol](https://img.shields.io/badge/protocol-Modbus%20TCP-orange)
![License](https://img.shields.io/badge/license-MIT-green)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5)](https://hacs.xyz)
![Validate](https://github.com/JH-Soft-Technology/acond-heatpump-ha/actions/workflows/validate.yml/badge.svg)

---

## 📸 Preview

| Desktop | Phone |
|---|---|
| ![Desktop](docs/preview-desktop-light.png) | ![Phone](docs/preview-mobile-dark.png) |

> Previews are rendered from the dashboard config with sample values; in Home Assistant the icons are real MDI icons and the fan spins while the compressor runs.

---

## ✨ Features

- **Modbus TCP** polling of all registers the Acond firmware exposes (input `30001–30018`, holding `40001–40012`) in two requests, set up from the UI
- **Sensors**: circuit 1 & 2 (actual / target), DHW (actual / target), flow water, return water (actual / target), outdoor air, brine, communication heartbeat
- **Status bits** from `TC_status` decoded into binary sensors: running, compressor, fault, DHW heating, circulation, defrost, backup heater (bivalence), summer mode, cooling
- **Control**:
  - `climate` thermostats for circuit 1, circuit 2 (optional) and DHW, with heating/idle action (target temperature written to holding registers)
  - `select` for heat pump mode (Auto / Heat pump only / Backup only / Off / Cooling) — preserves the other bits of `TC_set`
  - `select` for regulation type (AcondTherm / Equithermal / Manual)
  - `number` for manual return-water target
- **Dashboard view**:
  - illustrated schematic with live values: red = actual, green = target
  - separate layouts for desktop and phone (switches at 768 px)
  - spinning fan animation while the compressor runs, fault banner
  - tap a temperature to open its thermostat, tap mode/regulation icons to change them
  - 24 h history graphs of temperatures and operation

---

## 📦 Contents

```
custom_components/acond_heatpump/   # the integration (installed by HACS)
  www/                              # dashboard SVGs, served at /acond_heatpump/...
  brand/                            # integration icon
dashboard/heat-pump-view.yaml       # Lovelace view (sections)
legacy/packages/acond.yaml          # old YAML-only variant (not needed with the integration)
docs/                               # preview images
```

---

## 🚀 Installation

### 1. Enable Modbus TCP on the heat pump
Open the heat pump web interface → **ModbusTCP** page and tick the **ModbusTCP** checkbox. The status shows `ModbusTCP false` until Home Assistant connects – that is expected.

> ⚠️ The heat pump accepts **only one Modbus master**. Make sure no other system polls it. If communication stops for longer than *MaxCommDataRefresh* (30 s by default), the heat pump falls back to its own regulation.

### 2. Install via HACS
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JH-Soft-Technology&repository=acond-heatpump-ha&category=integration)

Or manually: **HACS → ⋮ → Custom repositories** → `https://github.com/JH-Soft-Technology/acond-heatpump-ha`, type **Integration** → download **Acond Heat Pump** → restart Home Assistant.

<details><summary>Manual installation without HACS</summary>

Copy `custom_components/acond_heatpump` to `/config/custom_components/` and restart Home Assistant.
</details>

### 3. Add the integration
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=acond_heatpump)

**Settings → Devices & services → Add integration → Acond Heat Pump** and fill in:

| Field | Default | Note |
|---|---|---|
| Host | – | IP address of the heat pump |
| Port | `502` | |
| Modbus device ID | `1` | ID `2` is reserved for cascades |
| Polling interval | `10 s` | 5–25 s, must stay below *MaxCommDataRefresh* |
| Heating circuit 2 | off | adds circuit 2 thermostat and sensors |
| Brine circuit | off | ground/water units only |

Polling interval and optional circuits can be changed later under **Configure**.

### 4. Add the dashboard view
Open your dashboard → **⋮ → Edit dashboard → ⋮ → Raw configuration editor** and paste the contents of `dashboard/heat-pump-view.yaml` as a new item under `views:`. The images are served by the integration, nothing has to be copied to `/config/www`.

### Migrating from the YAML package (v1.x)
1. Remove `/config/packages/acond.yaml` (and `/config/www/acond/` if you like) and restart Home Assistant.
2. Delete the orphaned `acond_*` entities under **Settings → Entities** (filter *Read-only*), otherwise the new ones get a `_2` suffix.
3. Install the integration as above. Entity IDs are the same as in v1, so dashboards and automations keep working.
4. In the dashboard, change image paths from `/local/acond/` to `/acond_heatpump/`.

Select states are now language-independent keys: mode `auto` / `heat_pump` / `backup` / `off` / `cooling`, regulation `acondtherm` / `equitherm` / `manual`. Update automations that compared against the old Czech labels.

---

## 🔢 Register map

Addresses are **0-based** on the wire (`30001` → input `0`, `40001` → holding `0`). Temperatures are `int16 × 10`, big endian.

| Register | HA address | Meaning | Entity |
|---|---|---|---|
| 30001 | input 0 | Circuit 1 target | `sensor.acond_okruh_1_zadana` |
| 30002 | input 1 | Circuit 1 actual | `sensor.acond_okruh_1_aktualni` |
| 30003 | input 2 | Circuit 2 target | `sensor.acond_okruh_2_zadana` |
| 30004 | input 3 | Circuit 2 actual | `sensor.acond_okruh_2_aktualni` |
| 30005 | input 4 | DHW target | `sensor.acond_tuv_zadana` |
| 30006 | input 5 | DHW actual | `sensor.acond_tuv_aktualni` |
| 30007 | input 6 | `TC_status` bit field | `sensor.acond_tc_status` → binary sensors |
| 30008 | input 7 | Return water target | `sensor.acond_zpatecka_zadana` |
| 30009 | input 8 | Return water actual | `sensor.acond_zpatecka_aktualni` |
| 30010 | input 9 | Outdoor air | `sensor.acond_venkovni_teplota` |
| 30014 | input 13 | Mode (0 auto, 1 HP, 3 backup, 4 off, 5 manual, 6 cooling) | `sensor.acond_rezim` |
| 30015 | input 14 | Regulation (0 AcondTherm, 1 equithermal, 2 manual) | `sensor.acond_typ_regulace` |
| 30016 | input 15 | Brine (ground/water units) | `sensor.acond_solanka` |
| 30017 | input 16 | Heartbeat counter 0–255 | `sensor.acond_heartbeat` |
| 30018 | input 17 | Flow (outlet) water | `sensor.acond_vystupni_voda` |
| 40001 | holding 0 | Circuit 1 target (write) | `climate.acond_okruh_1` |
| 40005 | holding 4 | DHW target (write) | `climate.acond_tuv` |
| 40006 | holding 5 | `TC_set` mode bits (write) | `select.acond_rezim_tc`, `sensor.acond_tc_set_raw` (disabled by default) |
| 40007 | holding 6 | Regulation type (write) | `select.acond_typ_regulace` |
| 40008 | holding 7 | Manual return target (write) | `number.acond_zpatecka_manual` |

`TC_status` bits: `0` on · `1` compressor · `2` fault · `3` DHW · `4` circulation 1 · `8` defrost · `9` backup heater · `10` summer · `12` cooling.

---

## ⚠️ Notes

- Entity IDs are fixed to the Czech-based IDs (e.g. `sensor.acond_tuv_aktualni`) so the dashboard works in any language; friendly names follow the HA language (English/Czech). If you rename entities, update the dashboard.
- Writes (`climate`, `select`, `number`) go straight to the heat pump. Test with small changes first.
- After changing an SVG, bump the `?v=` query in the dashboard so browsers don't serve the cached copy (images are cached).
- Circuit 2 and brine entities are only created when enabled in the integration options.

---

## 📄 License

[MIT](LICENSE)

---

[![buy me a coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jhoralek)
