# Ambient Lockit

Professional timecode synchronization tools for Ambient Lockit devices, providing both HID and MIDI connection management for broadcast and film production environments.

## Overview

The Ambient Lockit component provides comprehensive tools for interfacing with Ambient Lockit timecode generators and readers. It supports both HID (Human Interface Device) and MIDI communication protocols, enabling precise timecode synchronization in professional media production workflows.

## Features

- **HID Communication**: Direct USB communication with Lockit devices
- **MIDI Integration**: MIDI timecode (MTC) support for audio/video synchronization
- **Frame Rate Management**: Support for multiple frame rates (23.976, 24, 25, 29.97, 30, 47.96, 48, 50, 59.94, 60)
- **ACN Protocol**: Art-Net Control Network support for lighting integration
- **LTC Callback**: Linear Time Code callback functionality
- **Device Management**: Automatic device detection and connection handling
- **Configurable**: All device IDs and network settings can be customized

## Directory Structure

```
Ambient Lockit/
├── hid connection/          # HID device communication
│   ├── ambient.js          # Main HID library for Lockit devices
│   ├── runambient.js       # Example usage and testing
│   ├── draft.js            # Development/testing scripts
│   ├── UDPserver.js        # UDP server for network communication
│   ├── ACN_API.py          # Art-Net Control Network API
│   └── ACN-CL.py           # ACN command line interface
├── midi_connection/         # MIDI device communication
│   ├── midiTC.py           # MIDI timecode implementation
│   └── midi-hid.c          # MIDI to HID bridge (C implementation)
└── test2.py                # Basic HID device testing
```

## Configuration

All device IDs and network settings are configurable through environment variables or the centralized `config.py` file.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HID_VENDOR_ID` | `0x10E6` | HID device vendor ID |
| `HID_PRODUCT_ID` | `0x108C` | HID device product ID |
| `UDP_IP` | `127.0.0.1` | UDP server IP address |
| `UDP_PORT` | `41234` | UDP server port |

### Example Configuration

```bash
# Set environment variables for your specific devices
export HID_VENDOR_ID="0x10E6"
export HID_PRODUCT_ID="0x108C"
export UDP_IP="192.168.1.100"
export UDP_PORT="5000"
```

## Usage

### Basic HID Testing

Test basic HID device connectivity:

```bash
cd "Ambient Lockit"
python test2.py
```

This script will:
- Attempt to connect to a Lockit device using configurable VID/PID
- Read data from the device
- Display connection status and data
- Show current configuration settings

### HID Connection Management

#### JavaScript Implementation

```javascript
const ACNLockitLib = require('./hid connection/ambient');
const ACNLockit = new ACNLockitLib();

// Set frame rate (0-11 for different frame rates)
ACNLockit.setFrameFormat(3);  // 29.97 fps

// Get current frame rate
ACNLockit.getFrameFormat();

// Get sync status
ACNLockit.getSync();

// Set sync format
ACNLockit.setSyncFormat(1, 4, 6);

// Reset device
ACNLockit.reset();

// Get/set ACN channel
ACNLockit.getACNChannel();
ACNLockit.setACNChannel(12);

// Enable LTC callback
ACNLockit.LTCCallback(1);

// Reset timecode
ACNLockit.resetTime();

// Close device connection
ACNLockit.closedevice();
```

#### Running the Example

```bash
cd "Ambient Lockit/hid connection"
node runambient.js
```

### MIDI Timecode Integration

```python
cd "Ambient Lockit/midi_connection"
python midiTC.py
```

The MIDI implementation provides:
- MIDI timecode generation and reception
- Frame rate synchronization
- Real-time timecode display

### ACN (Art-Net Control Network) Support

```python
cd "Ambient Lockit/hid connection"
python ACN_API.py
```

ACN features:
- Network-based timecode distribution
- Lighting system integration
- Multi-device synchronization

## Frame Rate Support

The system supports the following frame rates:

| Index | Frame Rate | Description |
|-------|------------|-------------|
| 0     | 23.976     | Film (24fps with pulldown) |
| 1     | 24         | Film |
| 2     | 25         | PAL |
| 3     | 29.97      | NTSC |
| 4     | 30         | NTSC (drop frame) |
| 5     | 29.97 drop | NTSC drop frame |
| 6     | 30 drop    | 30fps drop frame |
| 7     | 47.96      | High frame rate |
| 8     | 48         | High frame rate |
| 9     | 50         | PAL high frame rate |
| 10    | 59.94      | NTSC high frame rate |
| 11    | 60         | High frame rate |

## Device Communication

### HID Protocol

The HID implementation communicates directly with Lockit devices via USB:

- **Vendor ID**: Configurable (default: 0x10E6)
- **Product ID**: Configurable (default: 0x108C)
- **Data Format**: 64-byte packets
- **Communication**: Bidirectional read/write

### MIDI Protocol

MIDI timecode (MTC) implementation:

- **Quarter Frame Messages**: 8 messages per frame
- **Full Frame Messages**: Complete timecode data
- **SMPTE Format**: Standard timecode format support

## Error Handling

The system includes comprehensive error handling:

- Device connection failures
- Communication timeouts
- Invalid frame rate settings
- MIDI port conflicts
- Configuration validation

## Troubleshooting

### Common Issues

1. **Device Not Found**
   - Ensure Lockit device is connected via USB
   - Check device drivers are installed
   - Verify VID/PID match your device in config
   - Update environment variables if needed

2. **Permission Errors**
   - Run with administrator privileges
   - Check USB device permissions
   - Ensure no other applications are using the device

3. **MIDI Port Issues**
   - Check MIDI device connections
   - Verify MIDI drivers are installed
   - Ensure correct port selection

4. **Configuration Issues**
   - Check environment variables are set correctly
   - Verify config.py file is accessible
   - Ensure device IDs match your hardware

### Debug Mode

Enable debug output by setting the DEBUG environment variable:

```bash
export DEBUG=true
python test2.py
```

## API Reference

### JavaScript API (ambient.js)

- `setFrameFormat(format)` - Set frame rate
- `getFrameFormat()` - Get current frame rate
- `getSync()` - Get synchronization status
- `setSyncFormat(format, param1, param2)` - Set sync format
- `reset()` - Reset device
- `getACNChannel()` - Get ACN channel
- `setACNChannel(channel)` - Set ACN channel
- `LTCCallback(enable)` - Enable/disable LTC callback
- `resetTime()` - Reset timecode
- `closedevice()` - Close device connection

### Python API (midiTC.py)

- `MidiTC()` - MIDI timecode class
- `start_mtc()` - Start MIDI timecode
- `stop_mtc()` - Stop MIDI timecode
- `set_frame_rate(rate)` - Set frame rate
- `get_current_timecode()` - Get current timecode

## Contributing

1. Test with your specific Lockit device model
2. Verify frame rate compatibility
3. Test MIDI integration with your setup
4. Document any device-specific requirements
5. Update configuration examples for new devices

## License

[Add your license information here]

## Support

For technical support:
- Check device compatibility
- Review error messages
- Test with different frame rates
- Verify USB/MIDI connections
- Check configuration settings