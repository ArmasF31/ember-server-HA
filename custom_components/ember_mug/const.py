"""Constants for the Ember Mug integration."""

DOMAIN = "ember_mug"
PLATFORMS = ["sensor"]

CONF_ADDRESS = "address"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DEVICE_TYPE = "device_type"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_DEVICE_TYPE = "mug"

DEVICE_TYPE_MUG = "mug"
DEVICE_TYPE_TUMBLER = "tumbler"
DEVICE_TYPES = [DEVICE_TYPE_MUG, DEVICE_TYPE_TUMBLER]

SERVICE_UUID = "fc543622-236c-4c94-8fa9-944a3e5353fa"

CHAR_CURRENT_TEMP = "fc540002-236c-4c94-8fa9-944a3e5353fa"
CHAR_TARGET_TEMP = "fc540003-236c-4c94-8fa9-944a3e5353fa"
CHAR_LIQUID_LEVEL = "fc540005-236c-4c94-8fa9-944a3e5353fa"
CHAR_BATTERY = "fc540007-236c-4c94-8fa9-944a3e5353fa"
CHAR_LIQUID_STATE = "fc540008-236c-4c94-8fa9-944a3e5353fa"
CHAR_PUSH_EVENTS = "fc540012-236c-4c94-8fa9-944a3e5353fa"

LIQUID_STATES = {
    1: "empty",
    2: "filling",
    3: "unknown",
    4: "cooling",
    5: "heating",
    6: "stable_temperature",
}
