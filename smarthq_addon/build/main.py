#!/usr/bin/env python3
"""
SmartHQ Appliance Control Add-on

Main application that runs the SmartHQ client and provides REST API
for Home Assistant integration.
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings
from pydantic_settings import BaseSettings

from smarthq_client import SmartHQClient, SmartHQDevice, SmartHQService, ServiceType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment variables."""
    username: str
    password: str
    region: str = "US"
    websocket_url: str = "wss://ws-us-west-2mysmarthq.com"
    enable_alerts: bool = True
    enable_services: bool = True
    enable_presence: bool = True
    enable_commands: bool = True
    log_level: str = "INFO"
    reconnect_interval: int = 30
    heartbeat_interval: int = 60
    host: str = "0.0.0.0"
    port: int = 8080

    class Config:
        env_file = ".env"


class CommandRequest(BaseModel):
    """Request model for sending commands to devices."""
    command: str
    data: List[Any] = []


class DeviceResponse(BaseModel):
    """Response model for device information."""
    device_id: str
    device_type: str
    name: str
    online: bool
    last_seen: Optional[str] = None
    services: Dict[str, Dict[str, Any]] = {}


class ServiceResponse(BaseModel):
    """Response model for service information."""
    service_id: str
    service_type: str
    domain_type: str
    device_id: str
    state: Dict[str, Any]
    config: Dict[str, Any]
    supported_commands: List[str]
    last_sync_time: str
    last_state_time: str


class SmartHQAddon:
    """SmartHQ add-on application."""
    def __init__(self):
        self.settings = Settings()
        self.client: SmartHQClient = None
        self.app = FastAPI(
            title="SmartHQ Appliance Control",
            description="REST API for SmartHQ appliance control and monitoring",
            version=1.0.0
        )
        self._setup_routes()
        self._setup_middleware()
        self._setup_event_handlers()
    
    def _setup_middleware(self):
        """Set up CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Set up API routes."""
        @self.app.get("/")
        async def root():
            """Root endpoint with basic info."""
            return {
                "name": "SmartHQ Appliance Control",
                "version": "1.0.0",
                "status": "running",
                "connected": self.client.connected if self.client else False
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "connected": self.client.connected if self.client else False,
                "device_count": len(self.client.devices) if self.client else 0
            }
        
        @self.app.get("/devices", response_model=List[DeviceResponse])
        async def get_devices():
            """Get all devices."""
            if not self.client:
                raise HTTPException(status_code=503, detail="Client not initialized")
            
            devices = []
            for device in self.client.devices.values():
                devices.append(DeviceResponse(
                    device_id=device.device_id,
                    device_type=device.device_type,
                    name=device.name,
                    online=device.online,
                    last_seen=device.last_seen.isoformat() if device.last_seen else None,
                    services=device.services
                ))
            return devices
        
        @self.app.get("/devices/{device_id}", response_model=DeviceResponse)
        async def get_device(device_id: str):
            """Get a specific device."""
            if not self.client:
                raise HTTPException(status_code=503, detail="Client not initialized")
            
            device = self.client.get_device(device_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            
            return DeviceResponse(
                device_id=device.device_id,
                device_type=device.device_type,
                name=device.name,
                online=device.online,
                last_seen=device.last_seen.isoformat() if device.last_seen else None,
                services=device.services
            )
        
        @self.app.get("/services", response_model=List[ServiceResponse])
        async def get_services():
            """Get all services."""
            if not self.client:
                raise HTTPException(status_code=503, detail="Client not initialized")
            
            services = []
            for service in self.client.services.values():
                services.append(ServiceResponse(
                    service_id=service.service_id,
                    service_type=service.service_type.value,
                    domain_type=service.domain_type,
                    device_id=service.device_id,
                    state=service.state,
                    config=service.config,
                    supported_commands=service.supported_commands,
                    last_sync_time=service.last_sync_time.isoformat(),
                    last_state_time=service.last_state_time.isoformat()
                ))
            return services
        
        @self.app.get("/services/{service_id}", response_model=ServiceResponse)
        async def get_service(service_id: str):
            """Get a specific service."""
            if not self.client:
                raise HTTPException(status_code=503, detail="Client not initialized")
            
            service = self.client.get_service(service_id)
            if not service:
                raise HTTPException(status_code=404, detail="Service not found")
            
            return ServiceResponse(
                service_id=service.service_id,
                service_type=service.service_type.value,
                domain_type=service.domain_type,
                device_id=service.device_id,
                state=service.state,
                config=service.config,
                supported_commands=service.supported_commands,
                last_sync_time=service.last_sync_time.isoformat(),
                last_state_time=service.last_state_time.isoformat()
            )
        
        @self.app.post("/devices/{device_id}/command")
        async def send_command(device_id: str, command_request: CommandRequest, background_tasks: BackgroundTasks):
            """Send a command to a device."""
            if not self.client:
                raise HTTPException(status_code=503, detail="Client not initialized")
            
            if not self.client.connected:
                raise HTTPException(status_code=503, detail="Not connected to SmartHQ")
            
            device = self.client.get_device(device_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            
            try:
                # Send command in background to avoid blocking
                background_tasks.add_task(
                    self.client.send_command,
                    device_id,
                    command_request.command,
                    command_request.data
                )
                
                return {
                    "status": "command_sent",
                    "device_id": device_id,
                    "command": command_request.command,
                    "data": command_request.data
                }
            except Exception as e:
                logger.error(f"Failed to send command: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to send command: {str(e)}")
        
        @self.app.get("/devices/{device_id}/services")
        async def get_device_services(device_id: str):
            """Get all services for a specific device."""
            if not self.client:
                raise HTTPException(status_code=503, detail="Client not initialized")
            
            device = self.client.get_device(device_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            
            services = []
            for service in self.client.services.values():
                if service.device_id == device_id:
                    services.append(ServiceResponse(
                        service_id=service.service_id,
                        service_type=service.service_type.value,
                        domain_type=service.domain_type,
                        device_id=service.device_id,
                        state=service.state,
                        config=service.config,
                        supported_commands=service.supported_commands,
                        last_sync_time=service.last_sync_time.isoformat(),
                        last_state_time=service.last_state_time.isoformat()
                    ))
            return services
    
    def _setup_event_handlers(self):
        """Set up SmartHQ client event handlers."""
        async def on_device_added(device: SmartHQDevice):
            """Handle device added event."""
            logger.info(f"Device added: {device.device_id} ({device.device_type})")
        
        async def on_device_updated(device: SmartHQDevice):
            """Handle device updated event."""
            logger.debug(f"Device updated: {device.device_id}")
        
        async def on_service_updated(service: SmartHQService):
            """Handle service updated event."""
            logger.debug(f"Service updated: {service.service_id} ({service.service_type.value})")
        
        async def on_alert_received(alert_data: Dict[str, Any]):
            """Handle alert received event."""
            logger.info(f"Alert received: {alert_data}")
        
        async def on_presence_changed(device_id: str, presence: Dict[str, Any]):
            """Handle presence changed event."""
            logger.info(f"Presence changed for {device_id}: {presence}")
        
        async def on_connected():
            """Handle connected event."""
            logger.info("Connected to SmartHQ")
        
        async def on_disconnected():
            """Handle disconnected event."""
            logger.warning("Disconnected from SmartHQ")
        
        # Store handlers for later assignment
        self._event_handlers = {
            "device_added": on_device_added,
            "device_updated": on_device_updated,
            "service_updated": on_service_updated,
            "alert_received": on_alert_received,
            "presence_changed": on_presence_changed,
            "connected": on_connected,
            "disconnected": on_disconnected,
        }
    
    async def start_client(self):
        """Start the SmartHQ client."""
        logger.info("Starting SmartHQ client...")
        
        self.client = SmartHQClient(
            username=self.settings.username,
            password=self.settings.password,
            region=self.settings.region,
            websocket_url=self.settings.websocket_url,
            enable_alerts=self.settings.enable_alerts,
            enable_services=self.settings.enable_services,
            enable_presence=self.settings.enable_presence,
            enable_commands=self.settings.enable_commands,
        )
        
        # Add event handlers
        for event, handler in self._event_handlers.items():
            self.client.add_event_handler(event, handler)
        
        # Connect to SmartHQ
        if not await self.client.connect():
            logger.error("Failed to connect to SmartHQ")
            return False
        
        logger.info("SmartHQ client started successfully")
        return True
    
    async def stop_client(self):
        """Stop the SmartHQ client."""
        if self.client:
            logger.info("Stopping SmartHQ client...")
            await self.client.disconnect()
            self.client = None
            logger.info("SmartHQ client stopped")
    
    async def run(self):
        """Run the application."""
        logger.info("Starting SmartHQ Appliance Control Add-on...")
        
        # Start the client
        if not await self.start_client():
            logger.error("Failed to start SmartHQ client")
            return
        
        # Start the FastAPI server
        config = uvicorn.Config(
            self.app,
            host=self.settings.host,
            port=self.settings.port,
            log_level=self.settings.log_level.lower(),
            access_log=True
        )
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.stop_client()
            logger.info("SmartHQ Appliance Control Add-on stopped")


async def main():
    """Entry point."""
    addon = SmartHQAddon()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await addon.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 