"""Constants for the MaxVapor integration."""

DOMAIN = "maxvapor"

DEFAULT_BASE_URL = "https://dashboard.maxvapor.com/api/v1"

# Devices publish telemetry about once a second; polling the cloud state
# endpoint every 10 s keeps the dashboard fair-use guidance comfortable
# while staying responsive enough for a thermostat-style device.
UPDATE_INTERVAL_S = 10

# Mirrors the firmware's READY chip band: within 5 C of the setpoint while
# the heat is on.
READY_BAND_C = 5.0

# The device UI tops out at 850 F.
MAX_TEMP_C = 454.4
