artHQ Event Stream API Client

Implements the SmartHQ Event Stream API (AsyncAPI 2.60 for real-time
appliance control and monitoring.
"

import asyncio
import json
import logging
import ssl
import websockets
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    rtHQ service types from the AsyncAPI spec"
    TEMPERATURE = "cloud.smarthq.service.temperature"
    TOGGLE = "cloud.smarthq.service.toggle"
    MODE = "cloud.smarthq.service.mode"
    METER = "cloud.smarthq.service.meter"
    CYCLE_TIMER = "cloud.smarthq.service.cycletimer"
    INTEGER = "cloud.smarthq.service.integer"
    STRING = "cloud.smarthq.service.string PROVIDER = "cloud.smarthq.service.provider"
    COLOR = "cloud.smarthq.service.color"
    TRIGGER = "cloud.smarthq.service.trigger"
    COOKING_STATE_V1ud.smarthq.service.cooking.state.v1    COOKING_MODE_V1ud.smarthq.service.cooking.mode.v1   COOKING_HISTORY = "cloud.smarthq.service.cooking.history    COOKING_BURNER_STATUS_V1ud.smarthq.service.cooking.burner.status.v1
    THERMOSTAT_V1ud.smarthq.service.thermostat.v1
    FIRMWARE_V1ud.smarthq.service.firmware.v1    LAUNDRY_COMMERCIAL_V1ud.smarthq.service.laundry.commercial.v1
class MessageKind(Enum):
  Message kinds from the AsyncAPI spec"    WEBSOCKET_PONG =websocket#pong"
    WEBSOCKET_CONNECTION = "websocket#connection"
    COMMAND = command  PRESENCE = presence"
    DEVICE = device"
    ALERT = "alert"
    SERVICE =pubsub#service"
    WEBSOCKET_PING =websocket#ping"
    WEBSOCKET_PUBSUB =websocket#pubsub"
    USER_PUBSUB =user#pubsub"


@dataclass
class SmartHQDevice:
 Represents a SmartHQ device/appliance    device_id: str
    device_type: str
    name: str
    services: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    online: bool = False
    last_seen: Optional[datetime] = None


@dataclass
class SmartHQService:
 Represents a SmartHQ service   service_id: str
    service_type: ServiceType
    domain_type: str
    device_id: str
    state: Dict[str, Any]
    config: Dict[str, Any]
    supported_commands: List[str]
    last_sync_time: datetime
    last_state_time: datetime


class SmartHQClient:
 
    SmartHQ Event Stream API Client
    
    Implements the AsyncAPI specification for real-time appliance control
    and monitoring via WebSocket connections.
     
    def __init__(
        self,
        username: str,
        password: str,
        region: str = US
        websocket_url: str = wss://ws-us-west-2rthq.com",
        enable_alerts: bool = True,
        enable_services: bool = True,
        enable_presence: bool = True,
        enable_commands: bool = True,
    ):
        self.username = username
        self.password = password
        self.region = region
        self.websocket_url = websocket_url
        self.enable_alerts = enable_alerts
        self.enable_services = enable_services
        self.enable_presence = enable_presence
        self.enable_commands = enable_commands
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = false       self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        
        # Device and service tracking
        self.devices: Dict[str, SmartHQDevice] = {}
        self.services: Dict[str, SmartHQService] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
         device_added:          device_updated:          device_removed:          service_updated:           alert_received:
           presence_changed:         command_result:       connected:,
         disconnected": [],
        }
        
        # Connection management
        self._reconnect_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._should_reconnect = True
        self._ssl_context = ssl.create_default_context()
        
    def add_event_handler(self, event: str, handler: Callable):
     d an event handler""       if event in self.event_handlers:
            self.event_handlers[event].append(handler)
        else:
            logger.warning(f"Unknown event type: {event}")
    
    def remove_event_handler(self, event: str, handler: Callable):
        e an event handler""       if event in self.event_handlers and handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
    
    async def _trigger_event(self, event: str, *args, **kwargs):
    igger all handlers for an event"""
        for handler in self.event_handlers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
    
    async def authenticate(self) -> bool:
       Authenticate with SmartHQ and get access token
        
        This would typically involve OAuth2 flow with SmartHQs authentication
        endpoints. For now, we'll assume the access token is provided.
         # TODO: Implement proper OAuth2 authentication flow
        # For now, we'll use a placeholder that would be replaced with
        # actual authentication logic
        try:
            # This would be replaced with actual OAuth2 authentication
            # await self._get_oauth2_token()
            # await self._get_websocket_credentials()
            logger.info("Authentication placeholder - implement OAuth2 flow")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    async def connect(self) -> bool:
   Connect to SmartHQ WebSocket" if self.connected:
            return true          
        try:
            # Authenticate first
            if not await self.authenticate():
                return False
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.websocket_url,
                ssl=self._ssl_context,
                extra_headers={
                    Authorization": f"Bearer {self.access_token}" if self.access_token else                 }
            )
            
            self.connected = True
            logger.info("Connected to SmartHQ WebSocket")
            
            # Start message processing
            asyncio.create_task(self._process_messages())
            
            # Configure subscriptions
            await self._configure_subscriptions()
            
            # Start heartbeat
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            await self._trigger_event("connected")
            return true          
        except Exception as e:
            logger.error(fFailed to connect: {e}")
            self.connected =false            return False
    
    async def disconnect(self):
        connect from SmartHQ WebSocket      self._should_reconnect = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.connected = False
        await self._trigger_event("disconnected")
        logger.info(Disconnected from SmartHQ WebSocket")
    
    async def _configure_subscriptions(self):
        vent subscriptions based on settings       config = {
            kind":websocket#pubsub",
           action": "pubsub",
          pubsub True,
           alerts": self.enable_alerts,
          services": self.enable_services,
          presence": self.enable_presence,
          commands": self.enable_commands,
        }
        
        await self._send_message(config)
        logger.info("Configured event subscriptions")
    
    async def _send_message(self, message: Dict[str, Any]):
       Senda message to SmartHQ       if not self.websocket or not self.connected:
            raise ConnectionError("Not connected to SmartHQ")
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def _process_messages(self):
ocess incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON message: {e})            except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connected =false
            await self._trigger_event("disconnected")
            
            if self._should_reconnect:
                await self._schedule_reconnect()
        except Exception as e:
            logger.error(f"Error in message processing: {e}")
            self.connected = False
    
    async def _handle_message(self, data: Dict[str, Any]):le different types of messages       kind = data.get("kind", "")
        
        if kind == MessageKind.WEBSOCKET_PONG.value:
            await self._handle_pong(data)
        elif kind == MessageKind.WEBSOCKET_CONNECTION.value:
            await self._handle_connection_response(data)
        elif kind == MessageKind.COMMAND.value:
            await self._handle_command_message(data)
        elif kind == MessageKind.PRESENCE.value:
            await self._handle_presence_message(data)
        elif kind == MessageKind.DEVICE.value:
            await self._handle_device_message(data)
        elif kind == MessageKind.ALERT.value:
            await self._handle_alert_message(data)
        elif kind == MessageKind.SERVICE.value:
            await self._handle_service_message(data)
        else:
            logger.debug(f"Unknown message kind: {kind}")
    
    async def _handle_pong(self, data: Dict[str, Any]):
    ndle pong response      logger.debug(f"Received pong: {data.get('id', 'unknown')}")
    
    async def _handle_connection_response(self, data: Dict[str, Any]):Handle connection response       logger.info("Received connection response")
        # Extract user_id and other connection details
        self.user_id = data.get(userId")
    
    async def _handle_command_message(self, data: Dict[str, Any]):
       dle command result message"""
        await self._trigger_event("command_result", data)
    
    async def _handle_presence_message(self, data: Dict[str, Any]):
        e presence message
        device_id = data.get("deviceId")
        presence = data.get("presence", {})
        
        if device_id in self.devices:
            self.devices[device_id].online = presence.get("online", false)
            self.devices[device_id].last_seen = datetime.fromisoformat(
                presence.get("lastSeen", ").replace("Z", "+000     )
            await self._trigger_event("presence_changed", device_id, presence)
    
    async def _handle_device_message(self, data: Dict[str, Any]):
      dle device message
        device_id = data.get("deviceId")
        device_type = data.get("deviceType")
        name = data.get("name", device_id)
        
        if device_id not in self.devices:
            # New device
            device = SmartHQDevice(
                device_id=device_id,
                device_type=device_type,
                name=name
            )
            self.devices[device_id] = device
            await self._trigger_event("device_added, device)
        else:
            # Update existing device
            self.devices[device_id].device_type = device_type
            self.devices[device_id].name = name
            await self._trigger_event("device_updated", self.devices[device_id])
    
    async def _handle_alert_message(self, data: Dict[str, Any]):
     ndle alert message"""
        await self._trigger_event("alert_received", data)
    
    async def _handle_service_message(self, data: Dict[str, Any]):
       le service message"        service_id = data.get("serviceId)      service_type = data.get("serviceType")
        device_id = data.get("deviceId")
        
        # Create or update service
        service = SmartHQService(
            service_id=service_id,
            service_type=ServiceType(service_type),
            domain_type=data.get("domainType"),
            device_id=device_id,
            state=data.get("state", {}),
            config=data.get("config", {}),
            supported_commands=data.get(supportedCommands", []),
            last_sync_time=datetime.fromisoformat(data.get(lastSyncTime", ").replace("Z", "+00:0,
            last_state_time=datetime.fromisoformat(data.get("lastStateTime", ").replace("Z", +00       )
        
        self.services[service_id] = service
        
        # Update device services
        if device_id in self.devices:
            self.devices[device_id].services[service_id] = data
        
        await self._trigger_event(service_updated", service)
    
    async def _heartbeat_loop(self):
      periodic heartbeat pings"""
        while self.connected:
            try:
                await asyncio.sleep(60)  # Send ping every 60 seconds
                if self.connected:
                    ping_message = {
                        kind:websocket#ping                 id": str(uuid.uuid4()),
                       action                   }
                    await self._send_message(ping_message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    async def _schedule_reconnect(self):
      ule a reconnection attempt"
        if self._reconnect_task and not self._reconnect_task.done():
            return
        
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def _reconnect_loop(self):
   tempt to reconnect with exponential backoff"
        delay =5art with5econds
        max_delay = 300 minutes
        
        while self._should_reconnect and not self.connected:
            try:
                logger.info(f"Attempting to reconnect in {delay} seconds...)             await asyncio.sleep(delay)
                
                if await self.connect():
                    logger.info("Successfully reconnected")
                    break
                
                delay = min(delay * 2, max_delay)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {e})             delay = min(delay * 2, max_delay)
    
    async def send_command(self, device_id: str, command: str, data: List[Any] = None):
       Send a command to a device       if not self.connected:
            raise ConnectionError("Not connected to SmartHQ")
        
        command_message = {
            kind":websocket#api",
           actionapi",
           host": api.mysmarthq.com",
            methodPOST",
           path: f"/v1/appliance/{device_id}/control/{command},
          id": str(uuid.uuid4()),
    body[object Object]
                kind": appliance#control,
            userId": self.user_id,
            applianceId": device_id,
                command": command,
             data": data or [],
                ackTimeout0
         delay": 0
            }
        }
        
        await self._send_message(command_message)
        logger.info(f"Sent command {command} to device {device_id}")
    
    def get_device(self, device_id: str) -> Optional[SmartHQDevice]:
        Get a device by ID       return self.devices.get(device_id)
    
    def get_service(self, service_id: str) -> Optional[SmartHQService]:
      et a service by ID       return self.services.get(service_id)
    
    def get_devices_by_type(self, device_type: str) -> List[SmartHQDevice]:
        Get all devices of a specific type    return [device for device in self.devices.values() if device.device_type == device_type]
    
    def get_services_by_type(self, service_type: ServiceType) -> List[SmartHQService]:
et all services of a specific type   return [service for service in self.services.values() if service.service_type == service_type] 