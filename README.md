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
