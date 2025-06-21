# Immortal

A comprehensive hardware interface development project consisting of three main components for professional audio/video production environments.

## Overview

Immortal is a collection of tools and applications designed for professional media production workflows, focusing on timecode synchronization, serial communication testing, and advanced Stream Deck integration.

## Project Components

### 1. [Ambient Lockit](./Ambient%20Lockit/)
Professional timecode synchronization tools for Ambient Lockit devices, including HID and MIDI connection management.

### 2. [Serial Loopback](./Serial%20Loopback/)
Serial communication testing and debugging utilities for COM port identification and loopback testing.

### 3. [Streamdeck +](./Streamdeck%20+/)
Advanced Stream Deck integration with UDP communication, multi-layer interfaces, and dynamic content management.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **Node.js**: 14.0 or higher (for JavaScript components)
- **Hardware**: 
  - Ambient Lockit device (for Ambient Lockit component)
  - Serial devices (for Serial Loopback component)
  - Stream Deck device (for Streamdeck + component)

## Dependencies

### Python Dependencies
- `hidapi` - HID device communication
- `pyserial` - Serial port communication
- `PIL/Pillow` - Image processing
- `streamdeck` - Stream Deck SDK
- `pycaw` - Windows audio control
- `msgpack` - Message serialization
- `requests` - HTTP requests

### JavaScript Dependencies
- Node.js HID libraries
- UDP communication modules

## Configuration

This project uses a centralized configuration system to avoid hardcoded sensitive information. All configurable parameters are stored in `config.py` and can be overridden with environment variables.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UDP_IP` | `127.0.0.1` | Target IP address for UDP communication |
| `UDP_PORT` | `41234` | UDP send port |
| `RECEIVE_PORT` | `41235` | UDP receive port |
| `HID_VENDOR_ID` | `0x10E6` | HID device vendor ID |
| `HID_PRODUCT_ID` | `0x108C` | HID device product ID |
| `DEFAULT_BAUDRATE` | `9600` | Default serial baud rate |
| `DEFAULT_TIMEOUT` | `1` | Default serial timeout |
| `ASSETS_PATH` | `Assets` | Path to Stream Deck assets |
| `DEBUG` | `False` | Enable debug mode |

### Example Configuration

```bash
# Set environment variables
export UDP_IP="192.168.1.100"
export UDP_PORT="5000"
export HID_VENDOR_ID="0x10E6"
export HID_PRODUCT_ID="0x108C"

# Run scripts
python "Ambient Lockit/test2.py"
```

### Important Note

This project was developed during a summer internship. Some configurations, IP addresses, and device identifiers may be specific to the development environment and should be adjusted for your use case.

## Usage

Each component has its own README with detailed usage instructions:

- [Ambient Lockit README](./Ambient%20Lockit/README.md)
- [Serial Loopback README](./Serial%20Loopback/README.md)
- [Streamdeck + README](./Streamdeck%20+/README.md)

## Project Structure

```
Lockit-HID/
├── Ambient Lockit/          # Timecode synchronization tools
│   ├── hid connection/      # HID device communication
│   └── midi_connection/     # MIDI device communication
├── Serial Loopback/         # Serial communication testing
├── Streamdeck +/           # Stream Deck integration
│   ├── Assets/             # Image assets
│   ├── presets/            # Preset configurations
│   └── final/              # Final implementations
└── hidapi.dll              # HID API library
```

## Acknowledgments

- Ambient for Lockit device specifications
- Elgato for Stream Deck SDK
- Open source community for various libraries and tools 

## Important Note
This project was developed during a summer internship. Some configurations, IP addresses, and device identifiers may be specific to the development environment and should be adjusted for your use case.
