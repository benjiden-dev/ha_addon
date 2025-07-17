# SmartHQ Add-on API Reference

This document describes the REST API provided by the SmartHQ Appliance Control add-on.

## Base URL

The add-on runs on port8080 default:
```
http://localhost:8080
```

## Authentication

Currently, the add-on uses the SmartHQ credentials configured in the add-on settings. Future versions may support API key authentication.

## Endpoints

### Root Endpoint

**GET /** - Get basic add-on information

**Response:**
```json
[object Object]name": SmartHQ Appliance Control,
 version": 100status": "running",
  connected: true
}
```

### Health Check

**GET /health** - Check add-on health status

**Response:**
```json
{
  status": "healthy",
 connected: true,
  device_count": 5
}
```

### Devices

**GET /devices** - Get all devices

**Response:**
```json  [object Object]   device_id: AA:BB:CC:DD:EE:FF",
  device_type":oven",
    name": "Kitchen Oven",
  online:true,
    last_seen: 2024115T10:30:00,services": {
      temp_service": [object Object]    service_id": "temp_service",
       service_type": "cloud.smarthq.service.temperature,    domain_type": "cloud.smarthq.domain.setpoint",
 state": {
          celsius: 180       fahrenheit": 3560        }
      }
    }
  }
]
```

**GET /devices/{device_id}** - Get specific device

**Parameters:**
- `device_id` (string): Device MAC address

**Response:** Same as device object in the devices list

### Services

**GET /services** - Get all services

**Response:**
```json
[object Object]
 service_id": "temp_service",
   service_type": "cloud.smarthq.service.temperature",
  domain_type": "cloud.smarthq.domain.setpoint",
   device_id: AA:BB:CC:DD:EE:FF,  state": [object Object]
      celsius: 180.0,
      fahrenheit": 356.0
      disabled": false
    },
   config": {
      celsiusMinimum": 500   celsiusMaximum": 2500,
  labelOven Temperature"
    },
    "supported_commands": ["set],  last_sync_time: 2024115T10:30,  last_state_time: 2024-115T10:300  }
]
```

**GET /services/{service_id}** - Get specific service

**Parameters:**
- `service_id` (string): Service identifier

**Response:** Same as service object in the services list

### Device Services

**GET /devices/{device_id}/services** - Get all services for a device

**Parameters:**
- `device_id` (string): Device MAC address

**Response:** Array of service objects for the specified device

### Commands

**POST /devices/{device_id}/command** - Send command to device

**Parameters:**
- `device_id` (string): Device MAC address

**Request Body:**
```json
{
  command": "set,data: [
    [object Object]
     celsius": 200
    }
  ]
}
```

**Response:**
```json
{
  status":command_sent",
 device_id: AA:BB:CC:DD:EE:FF",
  command": "set,data: [
    [object Object]
     celsius": 200
    }
  ]
}
```

## Service Types

The add-on supports the following SmartHQ service types:

### Temperature Service
- **Type:** `cloud.smarthq.service.temperature`
- **Purpose:** Temperature sensors and controls
- **State Properties:**
  - `celsius`: Temperature in Celsius
  - `fahrenheit`: Temperature in Fahrenheit
  - `celsiusConverted`: Converted Celsius value
  - `fahrenheitConverted`: Converted Fahrenheit value
  - `disabled`: Whether the service is disabled

### Toggle Service
- **Type:** `cloud.smarthq.service.toggle`
- **Purpose:** Binary on/off controls
- **State Properties:**
  - `on`: Boolean indicating if the device is on
  - `disabled`: Whether the service is disabled

### Mode Service
- **Type:** `cloud.smarthq.service.mode`
- **Purpose:** Mode selection (e.g., cooking modes)
- **State Properties:**
  - `mode`: Current mode string
  - `disabled`: Whether the service is disabled

### Meter Service
- **Type:** `cloud.smarthq.service.meter`
- **Purpose:** Energy/water consumption meters
- **State Properties:**
  - `meterValue`: Current meter reading
  - `meterValueDelta`: Change since last reading
  - `updateFrequencySeconds`: Update frequency
  - `disabled`: Whether the service is disabled

### Cycle Timer Service
- **Type:** `cloud.smarthq.service.cycletimer`
- **Purpose:** Cycle timers for appliances
- **State Properties:**
  - `secondsRemaining`: Time remaining in seconds
  - `secondsInitial`: Initial time in seconds
  - `paused`: Whether the timer is paused

### Thermostat Service
- **Type:** `cloud.smarthq.service.thermostat.v1`
- **Purpose:** Thermostat controls
- **State Properties:**
  - `on`: Whether the thermostat is on
  - `mode`: Current mode (heat, cool, auto, etc.)
  - `fanSpeed`: Fan speed setting
  - `coolCelsius`: Cool setpoint in Celsius
  - `heatCelsius`: Heat setpoint in Celsius
  - `humidity`: Current humidity percentage

## Error Responses

All endpoints may return the following error responses:

**503 Service Unavailable:**
```json
{
 detail": "Client not initialized
}
```

**404t Found:**
```json
{
 detail":Device not found"
}
```

**50ernal Server Error:**
```json
{
 detail: ed to send command: Connection error"
}
```

## WebSocket Events

The add-on also supports WebSocket connections for real-time updates. Connect to:

```
ws://localhost:8080/ws
```

### Event Types

- `device_added`: New device discovered
- `device_updated`: Device information updated
- `service_updated`: Service state changed
- `alert_received`: Alert notification received
- `presence_changed`: Device online/offline status changed
- `connected`: Connected to SmartHQ
- `disconnected`: Disconnected from SmartHQ

## Examples

### Set Oven Temperature

```bash
curl -X POST http://localhost:880/devices/AA:BB:CC:DD:EE:FF/command \
  -H "Content-Type: application/json" \
  -d[object Object]   command": set",
    data
      [object Object]       celsius":2000
      }
    ]
  }
```

### Turn On Dishwasher

```bash
curl -X POST http://localhost:880/devices/AA:BB:CC:DD:EE:FF/command \
  -H "Content-Type: application/json" \
  -d[object Object]   command": set",
    data
   [object Object]      on": true
      }
    ]
  }
```

### Get All Devices

```bash
curl http://localhost:8080vices
```

### Get Device Services

```bash
curl http://localhost:880/devices/AA:BB:CC:DD:EE:FF/services
``` 