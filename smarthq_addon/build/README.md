# SmartHQ Appliance Control Add-on

A Home Assistant add-on that provides real-time control and monitoring of SmartHQ-enabled appliances using the SmartHQ Event Stream API.

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

## Installation

1. Add this repository to your Home Assistant add-ons
2. Install the SmartHQ Appliance Control" add-on3nfigure your SmartHQ credentials
4. Start the add-on

## Configuration

```yaml
# Configuration options
username: "your_smarthq_username"
password: "your_smarthq_password"
region: "US"  # or other supported regions
websocket_url: wss://ws-us-west-2marthq.com"
enable_alerts: true
enable_services: true
enable_presence: true
enable_commands: true
```

## Supported Appliances

- **Cooking Appliances**: Ovens, microwaves, ranges
- **Laundry Appliances**: Washers, dryers
- **Kitchen Appliances**: Refrigerators, dishwashers
- **Climate Control**: Thermostats, water heaters
- **Other**: Any SmartHQ-enabled appliance

## API Integration

This add-on implements the SmartHQ Event Stream API (AsyncAPI2.6to provide:
- Real-time device state updates
- Remote control capabilities
- Event-driven architecture
- WebSocket-based communication

## Development

See the `docs/` directory for detailed development documentation. 