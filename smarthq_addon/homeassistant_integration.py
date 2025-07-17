istant Integration for SmartHQ

Provides REST sensor and switch entities for SmartHQ appliances
through the add-ons REST API.
"

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_RESOURCE,
    CONF_METHOD,
    CONF_HEADERS,
    CONF_PARAMS,
    CONF_VERIFY_SSL,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_ON,
    STATE_OFF,
    STATE_UNAVAILABLE,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.rest import RestData
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.light import LightEntity

logger = logging.getLogger(__name__)

DOMAIN =smarthq_addon
DEFAULT_NAME =SmartHQ"
DEFAULT_TIMEOUT = 10DEFAULT_SCAN_INTERVAL = 30nfiguration schema
CONFIG_SCHEMA = [object Object]  smarthq_addon": {
        addon_url": str,
       username": str,
       password: str,
    }
}


class SmartHQCoordinator(DataUpdateCoordinator):
    rdinator for SmartHQ add-on data."
    def __init__(self, hass: HomeAssistant, addon_url: str):
       ze the coordinator."""
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.addon_url = addon_url.rstrip("/")
        self.session = aiohttp.ClientSession()

    async def _async_update_data(self) -> Dict[str, Any]:
    te data from SmartHQ add-on."""
        try:
            # Get devices
            async with self.session.get(f{self.addon_url}/devices") as response:
                if response.status == 200:
                    devices = await response.json()
                else:
                    logger.error(f"Failed to get devices: {response.status}")
                    return[object Object]
            # Get services
            async with self.session.get(f{self.addon_url}/services") as response:
                if response.status == 200:
                    services = await response.json()
                else:
                    logger.error(f"Failed to get services: {response.status}")
                    services = []

            return[object Object]
                devices": devices,
         services": services,
            last_update": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Error updating SmartHQ data: {e}")
            return[object Object]    async def send_command(self, device_id: str, command: str, data: List[Any] = None) -> bool:
       Send a command to a device."""
        try:
            payload =[object Object]
                command": command,
             data": data or     }
            async with self.session.post(
                f{self.addon_url}/devices/{device_id}/command,              json=payload
            ) as response:
                if response.status == 200:
                    logger.info(fCommand {command} sent to device {device_id}")
                    return True
                else:
                    logger.error(f"Failed to send command: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False


class SmartHQDeviceEntity(Entity):
   se class for SmartHQ device entities."
    def __init__(self, coordinator: SmartHQCoordinator, device: Dict[str, Any]):
       tialize the entity."        self.coordinator = coordinator
        self.device = device
        self.device_id = device["device_id"]
        self._attr_name = device.get("name", device["device_id])        self._attr_unique_id = fsmarthq_{self.device_id}"

    @property
    def available(self) -> bool:
       urntruentity is available.       return self.device.get(online", False)

    @property
    def device_info(self) -> Dict[str, Any]:
      Return device info.
        return {
           identifiers": {(DOMAIN, self.device_id)},
            name: self._attr_name,
           manufacturer": "SmartHQ",
           model: self.device.get("device_type", "Unknown"),
        }


class SmartHQTemperatureSensor(SmartHQDeviceEntity, SensorEntity):
    """SmartHQ temperature sensor."
    def __init__(self, coordinator: SmartHQCoordinator, device: Dict[str, Any], service: Dict[str, Any]):
       ze the temperature sensor."""
        super().__init__(coordinator, device)
        self.service = service
        self.service_id = service["service_id"]
        self._attr_name = f{self._attr_name} Temperature"
        self._attr_unique_id = fsmarthq_{self.device_id}_temp"
        self._attr_device_class = "temperature"
        self._attr_native_unit_of_measurement = "°C"

    @property
    def native_value(self) -> Optional[float]:
   rn the temperature value."      state = self.service.get("state",[object Object]     # Try Celsius first, then Fahrenheit converted
        temp = state.get("celsius) orstate.get("celsiusConverted)        if temp is not None:
            return float(temp)
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
     Return extra state attributes."      state = self.service.get("state", [object Object]
        return {
       fahrenheit": state.get("fahrenheit),    fahrenheit_converted": state.get(fahrenheitConverted),          celsius_converted": state.get("celsiusConverted"),
           disabled": state.get("disabled, False),
        }


class SmartHQToggleSwitch(SmartHQDeviceEntity, SwitchEntity):
   rtHQ toggle switch."
    def __init__(self, coordinator: SmartHQCoordinator, device: Dict[str, Any], service: Dict[str, Any]):
       tialize the toggle switch."""
        super().__init__(coordinator, device)
        self.service = service
        self.service_id = service["service_id"]
        self._attr_name = f{self._attr_name} {service.get('domain_type,Toggle).split('.')[-1].title()}"
        self._attr_unique_id = fsmarthq_{self.device_id}_{self.service_id}"

    @property
    def is_on(self) -> bool:
       urn True if entity is on."      state = self.service.get("state", [object Object]      return state.get("on", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        Turn the entity on."       if "set" in self.service.get("supported_commands", []):
            await self.coordinator.send_command(self.device_id, "set", [{ontrue}])

    async def async_turn_off(self, **kwargs: Any) -> None:
        urn the entity off."       if "set" in self.service.get("supported_commands", []):
            await self.coordinator.send_command(self.device_id, "set, [{"on": False}])


class SmartHQModeSelect(SmartHQDeviceEntity, SensorEntity):
 martHQ mode select sensor."
    def __init__(self, coordinator: SmartHQCoordinator, device: Dict[str, Any], service: Dict[str, Any]):
       nitialize the mode select sensor."""
        super().__init__(coordinator, device)
        self.service = service
        self.service_id = service["service_id"]
        self._attr_name = f{self._attr_name} Mode"
        self._attr_unique_id = fsmarthq_{self.device_id}_{self.service_id}_mode"

    @property
    def native_value(self) -> Optional[str]:
   Return the current mode."      state = self.service.get("state", [object Object]      mode = state.get(mode)
        if mode:
            # Extract the last part of the mode string for display
            return mode.split(.")[-1].replace(_).title()
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
     Return extra state attributes.     config = self.service.get("config", [object Object]
        return {
            supported_modes": config.get("supportedModes",        disabled": self.service.get(state[object Object]}).get("disabled, False),
        }


class SmartHQMeterSensor(SmartHQDeviceEntity, SensorEntity):
  artHQ meter sensor."
    def __init__(self, coordinator: SmartHQCoordinator, device: Dict[str, Any], service: Dict[str, Any]):
       itialize the meter sensor."""
        super().__init__(coordinator, device)
        self.service = service
        self.service_id = service["service_id"]
        self._attr_name = f{self._attr_name} Meter"
        self._attr_unique_id = fsmarthq_{self.device_id}_{self.service_id}_meter"

    @property
    def native_value(self) -> Optional[float]:
   rn the meter value."      state = self.service.get("state", [object Object]      return state.get(meterValue)
    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        Return the unit of measurement.     config = self.service.get("config",[object Object]})
        units = config.get(meterUnits", "")
        unit_map = {
        cloud.smarthq.type.meterunits.kwh": kWh",
        cloud.smarthq.type.meterunits.kw":kW",
        cloud.smarthq.type.meterunits.amps": A        cloud.smarthq.type.meterunits.volts": V        cloud.smarthq.type.meterunits.gallons": gal",
        cloud.smarthq.type.meterunits.liters: 
        }
        return unit_map.get(units, units.split(".")-1if units else None)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
     Return extra state attributes."      state = self.service.get("state", [object Object])
        config = self.service.get("config", [object Object]
        return {
            meter_value_delta": state.get("meterValueDelta"),
            update_frequency_seconds": state.get("updateFrequencySeconds"),
           disabled": state.get("disabled", False),
         reading_type": config.get("reading"),
           measurement_type": config.get("measurement"),
        }


def create_entities_from_services(coordinator: SmartHQCoordinator, device: Dict[str, Any]) -> List[Entity]:
    ate entities based on device services.    entities = services = device.get("services", {})

    for service_id, service_data in services.items():
        service_type = service_data.get("serviceType",        domain_type = service_data.get("domainType", "")

        # Temperature sensors
        if service_type == "cloud.smarthq.service.temperature":
            entities.append(SmartHQTemperatureSensor(coordinator, device, service_data))

        # Toggle switches
        elif service_type == "cloud.smarthq.service.toggle":
            entities.append(SmartHQToggleSwitch(coordinator, device, service_data))

        # Mode selects
        elif service_type == "cloud.smarthq.service.mode":
            entities.append(SmartHQModeSelect(coordinator, device, service_data))

        # Meter sensors
        elif service_type == "cloud.smarthq.service.meter":
            entities.append(SmartHQMeterSensor(coordinator, device, service_data))

    return entities


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
   et up SmartHQ from a config entry." addon_url = entry.data.get(addon_url", http://localhost:8080")
    
    coordinator = SmartHQCoordinator(hass, addon_url)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Create entities for each device
    entities =
    for device in coordinator.data.get("devices", []):
        device_entities = create_entities_from_services(coordinator, device)
        entities.extend(device_entities)
    
    # Add entities to Home Assistant
    if entities:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        # Add entities to appropriate platforms
        for entity in entities:
            if isinstance(entity, SensorEntity):
                hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, entry)
            elif isinstance(entity, SwitchEntity):
                hass.helpers.discovery.async_load_platform("switch", DOMAIN, {}, entry)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    oad a config entry."" if DOMAIN in hass.data:
        coordinator = hass.dataDOMAIN].pop(entry.entry_id)
        await coordinator.session.close()
    
    return True 