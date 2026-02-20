# Ember Mug Bluetooth Documentation

## Introduction

This repository contains a reverse-engineered documentation for the bluetooth API of [Ember Mugs](https://ember.com/).

The information provided here was retrieved using the Ember smartphone app on Android using an **Ember Mug 2** and decompiling the APK through [Java decompilers](http://www.javadecompilers.com/apk).

It may not be applicable to other Ember mugs, but feel free to extend the documentation and open a pull request :).

## Privacy

Data collected by the bluetooth gets sent to: [`https://collector.embertech.com`](https://collector.embertech.com)

Read [Data Collection & Privacy](./data-collection.md) for more information.

## Documentation

All commands have a service UUID of `fc543622236c4c948fa9944a3e5353fa`

* [Mug color](./docs/mug-color.md)
* [Target temperature](./docs/target-temp.md)
* [Current temperature](./docs/current-temp.md)
* [Battery percentage](./docs/battery.md)
* [Temperature unit](./docs/temperature-unit.md)
* [Liquid level](./docs/liquid-level.md)
* [Liquid state](./docs/liquid-state.md)
* [Mug name](./docs/mug-name.md)
* [Date & timezone](./docs/time-date-zone.md)
* [Push events](./docs/push-events.md)
* [Firmware & hardware versions](./docs/push-events.md)



## Home Assistant custom integration: Ember Mug Live

This repository now includes a Home Assistant custom integration under `custom_components/ember_mug`.

### Features

- Reads Ember Mug BLE values using the protocol docs in this repo:
  - Current temp (`fc540002-...`)
  - Target temp (`fc540003-...`)
  - Battery + charging (`fc540007-...`)
  - Liquid state (`fc540008-...`)
  - Liquid level (`fc540005-...`)
- Exposes those values as HA sensors.
- Hosts a tiny realtime page via Home Assistant HTTP at:
  - `/ember_mug` (human page)
  - `/api/ember_mug/status` (JSON snapshot)
  - `/api/ember_mug/events` (SSE realtime stream)

### Install

1. Copy `custom_components/ember_mug` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add integration **Ember Mug Live** from *Settings → Devices & Services*.
4. Select an auto-discovered Ember device (or choose manual entry and input MAC address).
5. Choose device type: **Mug** or **Tumbler**.

### Notes

- BLE range and adapter support apply (Home Assistant host needs BLE access).
- The integration polls by default every 15s (configurable via options).
- Automatic BLE discovery is supported during setup.
- Device type can be switched between Mug and Tumbler in integration options.
- The realtime webpage updates from SSE messages generated after coordinator refreshes.
