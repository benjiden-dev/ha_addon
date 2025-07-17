# SmartHQ Appliance Control Implementation Guide

This guide explains how to use the SmartHQ Event Stream API (AsyncAPI 2.60 specifications to build a Home Assistant add-on for controlling SmartHQ-enabled appliances.

## Overview

The SmartHQ Event Stream API provides real-time communication with SmartHQ-enabled appliances through WebSocket connections. This implementation creates a Home Assistant add-on that:

1. Connects to SmartHQ via WebSocket
2. Subscribes to real-time device updates
3rovides a REST API for Home Assistant integration
4. Creates Home Assistant entities for appliance control

## Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   SmartHQ API   │ ◄──────────────► │  SmartHQ Client │
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘
                                              │
                                              │ REST API
                                              ▼
┌─────────────────┐                 ┌─────────────────┐
│ Home Assistant  │ ◄──────────────► │  FastAPI Server │
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘
```

## Key Components

###1 SmartHQ Client (`smarthq_client.py`)

The core client that implements the AsyncAPI specification:

- **WebSocket Connection**: Manages connection to SmartHQ WebSocket endpoint
- **Message Processing**: Handles different message types from the API spec
- **Event System**: Provides event-driven architecture for device updates
- **Authentication**: Handles OAuth2 authentication flow
- **Reconnection**: Automatic reconnection with exponential backoff

#### Key AsyncAPI Features Implemented:

- **Pub/Sub Pattern**: Subscribe to specific event types
- **Message Types**: Handle all message kinds from the spec
- **Service Types**: Support for temperature, toggle, mode, meter, etc.
- **Real-time Updates**: Process live device state changes

###2 FastAPI Server (`main.py`)

Provides REST API for Home Assistant integration:

- **Device Management**: Get device information and status
- **Service Control**: Access and control device services
- **Command Interface**: Send commands to appliances
- **Health Monitoring**: Health checks and status endpoints

###3istant Integration (`homeassistant_integration.py`)

Creates Home Assistant entities from SmartHQ services:

- **Sensors**: Temperature, meter readings, mode displays
- **Switches**: On/off controls for appliances
- **Climate**: Thermostat controls
- **Lights**: Light controls for appliances

## AsyncAPI Specification Usage

### Understanding the Spec

The SmartHQ AsyncAPI spec defines:1 **Channels**: WebSocket endpoints for communication
2. **Messages**: Request/response message formats
3. **Schemas**: Data structures for devices and services
4**Service Types**: Different types of appliance services

### Key Message Types

From the AsyncAPI spec, we handle these message types:

```python
class MessageKind(Enum):
    WEBSOCKET_PONG =websocket#pong"
    WEBSOCKET_CONNECTION = "websocket#connection"
    COMMAND = command  PRESENCE = presence"
    DEVICE = device"
    ALERT = "alert"
    SERVICE =pubsub#service
```
### Service Types

The spec defines various service types that map to Home Assistant entities:

| Service Type | Home Assistant Entity | Purpose |
|--------------|----------------------|---------|
| `temperature` | Sensor | Temperature readings and controls |
| `toggle` | Switch | On/off controls |
| `mode` | Select | Mode selection (cooking modes, etc.) |
| `meter` | Sensor | Energy/water consumption |
| `cycletimer` | Sensor | Cycle timers |
| `thermostat.v1` | Climate | Thermostat controls |

## Implementation Steps

###1. Authentication

The AsyncAPI spec requires OAuth2 authentication. Implement the authentication flow:

```python
async def authenticate(self) -> bool:
 Authenticate with SmartHQ and get access token"""
    # TODO: Implement OAuth2 flow
    # 1. Get OAuth2 token
    # 2. Get WebSocket credentials
    # 3. Store access token
    pass
```

### 2. WebSocket Connection

Establish WebSocket connection using the spec's channel definition:

```python
async def connect(self) -> bool:Connect to SmartHQ WebSocket"""
    self.websocket = await websockets.connect(
        self.websocket_url,
        ssl=self._ssl_context,
        extra_headers={
            Authorization": f"Bearer {self.access_token}     }
    )
```

### 3. Message Processing

Process messages according to the AsyncAPI message schemas:

```python
async def _handle_message(self, data: Dict[str, Any]):
    "le different types of messages"   kind = data.get("kind, )
    
    if kind == MessageKind.SERVICE.value:
        await self._handle_service_message(data)
    elif kind == MessageKind.DEVICE.value:
        await self._handle_device_message(data)
    # ... handle other message types
```

### 4. Service State Management

Track device and service states based on the spec's schema definitions:

```python
@dataclass
class SmartHQService:
    service_id: str
    service_type: ServiceType
    domain_type: str
    device_id: str
    state: Dict[str, Any]  # From AsyncAPI schema
    config: Dict[str, Any]  # From AsyncAPI schema
    supported_commands: List[str]
    last_sync_time: datetime
    last_state_time: datetime
```

### 5 Command Sending

Send commands using the spec's command format:

```python
async def send_command(self, device_id: str, command: str, data: List[Any] = None):
   Send a command to a device"""
    command_message =[object Object]
        kind":websocket#api,
       action": "api,
       host": api.mysmarthq.com,
        method:POST,
       path: f"/v1/appliance/{device_id}/control/{command}",
      id": str(uuid.uuid4()),
body: {
            kind": appliance#control",
        userId": self.user_id,
        applianceId": device_id,
            command": command,
         data": data or,
            ackTimeout:10            delay:0       }
    }
    await self._send_message(command_message)
```

## Home Assistant Integration

### Entity Creation

Create Home Assistant entities based on service types:

```python
def create_entities_from_services(coordinator, device):
    ate entities based on device services    entities = []
    
    for service_id, service_data in device["services"].items():
        service_type = service_data.get("serviceType")
        
        if service_type == "cloud.smarthq.service.temperature":
            entities.append(SmartHQTemperatureSensor(coordinator, device, service_data))
        elif service_type == "cloud.smarthq.service.toggle":
            entities.append(SmartHQToggleSwitch(coordinator, device, service_data))
        # ... handle other service types
    
    return entities
```

### REST API Integration

Use the add-on's REST API to communicate with SmartHQ:

```python
class SmartHQCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self) -> Dict[str, Any]:
    te data from SmartHQ add-on"""
        async with self.session.get(f{self.addon_url}/devices") as response:
            devices = await response.json()
        
        async with self.session.get(f{self.addon_url}/services") as response:
            services = await response.json()
        
        return [object Object]          devices": devices,
     services": services,
        last_update": datetime.now(),
        }
```

## Configuration

### Add-on Configuration

Configure the add-on through Home Assistant:

```yaml
# config.yaml
options:
  username: your_smarthq_username
  password: your_smarthq_password
  region: "US  websocket_url: wss://ws-us-west-2rthq.com
  enable_alerts: true
  enable_services: true
  enable_presence: true
  enable_commands: true
```

### Home Assistant Configuration

Add the integration to Home Assistant:

```yaml
# configuration.yaml
smarthq_addon:
  addon_url: http://localhost:8080
```

## Testing

### Local Development1. Build the add-on:
   ```bash
   ./build.sh
   cd build
   ```

2. Configure environment:
   ```bash
   cp .env.template .env
   # Edit .env with your SmartHQ credentials
   ```

3un locally:
   ```bash
   ./run.sh
   ```

### API Testing

Test the REST API:

```bash
# Get all devices
curl http://localhost:880es

# Get specific device
curl http://localhost:880/devices/AA:BB:CC:DD:EE:FF

# Send command
curl -X POST http://localhost:880/devices/AA:BB:CC:DD:EE:FF/command \
  -H "Content-Type: application/json" \
  -d{"command": set", data": {"celsius: 200}]}'```

## Deployment

### Home Assistant Add-on

1. Install as local add-on:
   ```bash
   ./install-addon.sh
   ```

2stall through Home Assistant UI:
   - Go to Settings → Add-ons → Add-on Store
   - Click the three dots → Repositories
   - Add your add-on repository
   - Install SmartHQ Appliance Control"

### Docker Deployment

Build and run as Docker container:

```bash
./build-docker.sh
docker run -p 8080:8080--env-file .env smarthq-appliance-control:latest
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**: Check SmartHQ credentials and region
2. **Connection Issues**: Verify WebSocket URL and network connectivity
3. **Missing Devices**: Ensure devices are registered in SmartHQ app4**Command Failures**: Check device online status and supported commands

### Debugging

Enable debug logging:

```yaml
# In add-on configuration
log_level: DEBUG
```

Check logs:

```bash
# Add-on logs
docker logs smarthq-addon

# Home Assistant logs
tail -f /config/home-assistant.log
```

## Future Enhancements

1. **OAuth2 Implementation**: Complete OAuth2 authentication flow
2. **WebSocket Support**: Add WebSocket endpoint for real-time updates
3. **Advanced Controls**: Support for complex cooking modes and schedules
4. **Energy Monitoring**: Enhanced energy consumption tracking
5e App**: Companion mobile app for remote control

## Resources

- [SmartHQ Event Stream API Documentation](https://docs.smarthq.com/device-control-and-monitoring/real-time-device-updates/)
- [AsyncAPI Specification](https://www.asyncapi.com/)
- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Client Documentation](https://websockets.readthedocs.io/)

## Conclusion

This implementation demonstrates how to use the SmartHQ AsyncAPI specification to create a comprehensive Home Assistant add-on for appliance control. The modular architecture allows for easy extension and maintenance, while the REST API provides a clean interface for Home Assistant integration.

The key to success is understanding the AsyncAPI specification and mapping its concepts to Home Assistant entities. By following the patterns established in the spec, you can create a robust and reliable appliance control system. 