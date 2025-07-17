# SmartHQ Appliance Control

A Home Assistant integration that provides real-time control and monitoring of SmartHQ-enabled appliances using the SmartHQ Event Stream API.

## Features

- Real-time appliance state monitoring
- Remote control of appliances
- Support for multiple appliance types:
  - Ovens and microwaves
  - Refrigerators
  - Dishwashers
  - Washers and dryers
  - Water heaters
  - Thermostats
- WebSocket-based real-time updates
- Automatic reconnection handling
- Configurable event subscriptions

## Installation (Direct, No Docker)

1. **Clone this repository** to your Home Assistant NUC:
   ```bash
   git clone <this-repo-url>
   cd smarthq_addon
   ```
2. **Create and activate a Python virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Copy and edit the environment file:**
   ```bash
   cp .env.template .env
   # Edit .env and fill in your SmartHQ credentials and settings
   ```
5. **Run the integration:**
   ```bash
   python3 main.py
   ```

## Configuration

Edit the `.env` file with your SmartHQ credentials and options:

```
USERNAME=your_smarthq_username
PASSWORD=your_smarthq_password
REGION=US
WEBSOCKET_URL=wss://ws-us-west-2.mysmarthq.com
ENABLE_ALERTS=true
ENABLE_SERVICES=true
ENABLE_PRESENCE=true
ENABLE_COMMANDS=true
LOG_LEVEL=INFO
RECONNECT_INTERVAL=30
HEARTBEAT_INTERVAL=60
HOST=0.0.0.0
PORT=8080
```

## Supported Appliances

- **Cooking Appliances**: Ovens, microwaves, ranges
- **Laundry Appliances**: Washers, dryers
- **Kitchen Appliances**: Refrigerators, dishwashers
- **Climate Control**: Thermostats, water heaters
- **Other**: Any SmartHQ-enabled appliance

## API Integration

This integration implements the SmartHQ Event Stream API to provide:
- Real-time device state updates
- Remote control capabilities
- Event-driven architecture
- WebSocket-based communication

## Development

See the `docs/` directory for detailed development documentation. 