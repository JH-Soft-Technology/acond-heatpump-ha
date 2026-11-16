"""Constants and register map for the Acond heat pump integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "acond_heatpump"
MANUFACTURER: Final = "Acond"
MODEL: Final = "Acond Therm"

CONF_DEVICE_ID: Final = "device_id"
CONF_CIRCUIT2: Final = "circuit2"
CONF_BRINE: Final = "brine"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_PORT: Final = 502
DEFAULT_DEVICE_ID: Final = 1
# The heat pump drops back to its own regulation when no Modbus traffic
# arrives within MaxCommDataRefresh (30 s by default), so poll well below it.
DEFAULT_SCAN_INTERVAL: Final = 10
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 25

STATIC_URL: Final = "/acond_heatpump"

# Block sizes read every poll (0-based addresses)
INPUT_COUNT: Final = 18  # 30001..30018
HOLDING_COUNT: Final = 12  # 40001..40012

# ---- Input registers (30001 = index 0) ----
IN_T_SET_INDOOR1: Final = 0
IN_T_ACT_INDOOR1: Final = 1
IN_T_SET_INDOOR2: Final = 2
IN_T_ACT_INDOOR2: Final = 3
IN_T_SET_DHW: Final = 4
IN_T_ACT_DHW: Final = 5
IN_STATUS: Final = 6
IN_T_SET_RETURN: Final = 7
IN_T_ACT_RETURN: Final = 8
IN_T_AIR: Final = 9
IN_T_SOLAR: Final = 10
IN_T_POOL: Final = 11
IN_T_SET_POOL: Final = 12
IN_MODE: Final = 13
IN_REGULATION: Final = 14
IN_T_BRINE: Final = 15
IN_HEARTBEAT: Final = 16
IN_T_OUTLET: Final = 17

# ---- Holding registers (40001 = index 0) ----
HR_T_SET_INDOOR1: Final = 0
HR_T_ACT_INDOOR1: Final = 1
HR_T_SET_INDOOR2: Final = 2
HR_T_ACT_INDOOR2: Final = 3
HR_T_SET_DHW: Final = 4
HR_TC_SET: Final = 5
HR_REGULATION: Final = 6
HR_T_SET_RETURN: Final = 7

# ---- TC_status bits (30007) ----
BIT_ON: Final = 0
BIT_RUNNING: Final = 1
BIT_FAULT: Final = 2
BIT_DHW: Final = 3
BIT_CIRC1: Final = 4
BIT_CIRC2: Final = 5
BIT_SOLAR: Final = 6
BIT_POOL: Final = 7
BIT_DEFROST: Final = 8
BIT_AUX: Final = 9
BIT_SUMMER: Final = 10
BIT_BRINE: Final = 11
BIT_COOLING: Final = 12

# ---- TC_set (40006) ----
# Bits 6-8 (solar, pool, summer/winter) are kept when the mode is changed.
TC_SET_KEEP_MASK: Final = 0b1_1100_0000
MODE_WRITE_BITS: Final = {
    "auto": 1 << 0,
    "heat_pump": 1 << 1,
    "backup": 1 << 2,
    "off": 1 << 3,
    "cooling": 1 << 4,
}
# rezim_pan (30014) -> option
MODE_READ: Final = {0: "auto", 1: "heat_pump", 3: "backup", 4: "off", 5: "manual", 6: "cooling"}
MODE_OPTIONS: Final = ["auto", "heat_pump", "backup", "off", "manual", "cooling"]

REGULATION_OPTIONS: Final = ["acondtherm", "equitherm", "manual"]
