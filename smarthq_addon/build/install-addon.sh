#!/bin/bash
# Install SmartHQ Add-on in Home Assistant
set -e
ADDON_DIR="/config/addons/local/smarthq_appliance_control"
echo "Installing SmartHQ Add-on to Home Assistant..."
sudo mkdir -p "$ADDON_DIR"
sudo cp -r * "$ADDON_DIR/"
sudo chown -R homeassistant:homeassistant "$ADDON_DIR"
sudo chmod -R 755 "$ADDON_DIR"
echo "Add-on installed successfully!"
echo "You can now install it from the Home Assistant Add-ons page."
echo "Look for SmartHQ Appliance Control in the Local Add-ons section."
