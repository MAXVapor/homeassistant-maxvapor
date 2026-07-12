# MaxVapor for Home Assistant

Control and monitor your MaxVapor e-nail from Home Assistant. The
integration talks to the MaxVapor cloud over HTTPS, so it works from any
network your Home Assistant can browse the web from. No port forwarding, no
MQTT setup, nothing to expose.

## What you get

Each linked device shows up in Home Assistant as one device with:

- A **thermostat** (climate entity): see the live coil temperature, drag
  the target temperature, and switch the heat on or off. The action shows
  "heating" while climbing and "idle" once the coil is holding at
  temperature.
- A **Ready** binary sensor that turns on the moment the coil settles
  within 5 C of the setpoint, the same logic as the READY indicator on the
  device screen. Great for automations: announce it on a speaker, flash a
  light, send a notification.
- **Coil health sensors**: two problem-class sensors that mirror the
  device's coil protection (repeated faults, suspected coil damage).
- A **temperature sensor** for history graphs and an **auto-off remaining**
  countdown.

State updates every 10 seconds. Commands (setpoint, heat on/off) are
delivered to the device within about a second.

## Installation

### HACS (recommended)

1. In HACS, choose "Custom repositories" and add
   `https://github.com/MAXVapor/homeassistant-maxvapor` as an Integration.
2. Install "MaxVapor" and restart Home Assistant.

### Manual

Copy `custom_components/maxvapor/` into your Home Assistant `config`
directory and restart.

## Setup

1. Sign in at [dashboard.maxvapor.com](https://dashboard.maxvapor.com),
   open a device, choose View Data Logs, and generate a token under
   **Access tokens**.
2. In Home Assistant: Settings, then Devices and Services, then
   **Add Integration**, search for "MaxVapor", and paste the token.

All devices linked to your account appear automatically.

## Automation ideas

```yaml
# Announce when the nail is ready
trigger:
  - platform: state
    entity_id: binary_sensor.living_room_nail_ready
    to: "on"
action:
  - service: tts.speak
    data:
      message: "Nail is ready"
```

Prefer push over polling? The MaxVapor dashboard can also POST webhook
events (ready, coil warnings, auto-off warnings and more) to a Home
Assistant webhook trigger URL. See the Integrations page on the dashboard.

## Requirements

- Home Assistant 2024.4 or newer
- A MaxVapor device linked to your dashboard account, running firmware
  0.2.0 or newer for the coil health sensors (older firmware simply
  reports them as clear)
