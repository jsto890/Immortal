# Streamdeck +

Advanced Stream Deck integration with UDP communication, multi-layer interfaces, and dynamic content management for professional media production workflows.

## Overview

Streamdeck + is a comprehensive Stream Deck integration solution that extends the capabilities of Elgato Stream Deck devices with advanced features including UDP communication, multi-layer interfaces, dynamic content management, and real-time audio/video control integration.

## Features

- **Multi-Layer Interface**: Dynamic layer switching with context-aware controls
- **UDP Communication**: Real-time network communication for external system integration
- **Audio Control**: System volume and mute control with visual feedback
- **Dynamic Content**: Real-time image and text updates via network messages
- **Touchscreen Support**: Full utilization of Stream Deck + touchscreen capabilities
- **Dial Integration**: Advanced dial control for parameter adjustment
- **Preset Management**: Configurable presets for different workflows
- **Cross-Platform**: Support for Windows, macOS, and Linux
- **Configurable**: All network settings and device parameters can be customized

## Directory Structure

```
Streamdeck +/
├── Assets/                  # Image assets and fonts
│   ├── AovelSansRounded-rdDL.ttf
│   ├── google.png
│   ├── immortal.png
│   ├── long.png
│   ├── mute.png
│   ├── touch.jpg
│   ├── volume.png
│   └── whitesquare.jpg
├── presets/                 # Preset configurations
│   ├── final.py            # Final preset implementation
│   ├── finalpreset.js      # JavaScript preset version
│   ├── recevier.py         # UDP message receiver
│   ├── sender.js           # UDP message sender
│   ├── test.py             # Testing preset
│   ├── chasestream.py      # Chase preset (Python)
│   └── chaseudp.js         # Chase preset (JavaScript)
├── final/                   # Final implementations
│   ├── changestream.py     # Stream change implementation
│   ├── changeudp.js        # UDP change implementation
│   ├── picturestream.py    # Picture stream implementation
│   └── pictureudp.js       # Picture UDP implementation
├── interactive.py           # Main interactive application
├── interactlinux.py        # Linux-specific implementation
├── SendUDP.py              # UDP communication module
├── editstreamdeck.js       # Stream Deck editor (JavaScript)
├── editstreamdeck.py       # Stream Deck editor (Python)
├── picture.js              # Picture management
├── test_action.js          # Action testing
├── initialisedetails.js    # Initialization details (JavaScript)
├── initialisedetails.py    # Initialization details (Python)
├── draftlinux.py           # Linux draft implementation
└── yep.py                  # Utility functions
```

## Configuration

All network settings and device parameters are configurable through environment variables or the centralized `config.py` file.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UDP_IP` | `127.0.0.1` | Target IP address for UDP communication |
| `UDP_PORT` | `41234` | UDP send port |
| `RECEIVE_PORT` | `41235` | UDP receive port |
| `ASSETS_PATH` | `Assets` | Path to Stream Deck assets |
| `FONT_PATH` | `/usr/share/fonts/ttf/LiberationSans-Regular.ttf` | Font path |
| `TOUCHSCREEN_WIDTH` | `800` | Touchscreen width |
| `TOUCHSCREEN_HEIGHT` | `100` | Touchscreen height |
| `DEBUG` | `False` | Enable debug mode |

### Example Configuration

```bash
# Set environment variables for your network
export UDP_IP="192.168.1.100"
export UDP_PORT="5000"
export RECEIVE_PORT="5001"
export DEBUG="true"

# Run applications
python interactive.py
```

## Usage

### Basic Interactive Application

Run the main interactive application:

```bash
cd "Streamdeck +"
python interactive.py
```

Features:
- Volume control with dials
- Mute/unmute functionality
- Touchscreen integration
- Key customization
- Real-time feedback

### UDP Communication

#### Sending UDP Messages

```bash
python SendUDP.py
```

This application:
- Sends Stream Deck events over UDP
- Supports key, dial, and touchscreen events
- Configurable target IP and port
- MessagePack serialization for efficiency

#### Receiving UDP Messages

```bash
cd presets
python recevier.py
```

Features:
- Listens for incoming UDP messages
- Processes Stream Deck events
- Updates interface dynamically
- Supports remote control

### Multi-Layer Interface

#### Layer Management

The system supports up to 3 layers with different functionalities:

- **Layer 1**: Basic controls and power management
- **Layer 2**: Advanced controls and mode switching
- **Layer 3**: Specialized functions and presets

#### Layer Switching

```python
# Switch to layer 2
current_layer = 2
refresh_all_keys(deck)
update_touchscreen_image(deck)
```

### Preset System

#### Using Presets

```bash
cd presets
python final.py
```

Preset features:
- Pre-configured button layouts
- Dynamic content loading
- Network-based updates
- Customizable actions

#### Creating Custom Presets

1. Define key configurations
2. Set up dial mappings
3. Configure touchscreen layout
4. Add UDP communication

## API Reference

### Core Functions

#### Key Management

- `update_key_image(deck, key, state)` - Update key appearance
- `get_key_style(deck, key, state)` - Get key styling information
- `render_key_image(deck, icon, font, label)` - Generate key images

#### Dial Control

- `dial_change_callback(deck, dial, event, value)` - Handle dial events
- `set_dial_function(dial, function)` - Assign dial functions

#### Touchscreen

- `set_touchscreen_image(deck, image_path)` - Set touchscreen image
- `update_touchscreen_image(deck)` - Update touchscreen display
- `touchscreen_event_callback(deck, event, value)` - Handle touch events

#### UDP Communication

- `send_udp_message(data)` - Send UDP message
- `udp_listener()` - Listen for UDP messages
- `process_udp_message(data)` - Process incoming messages

### Event Types

#### Key Events

```python
{
    "type": "key_event",
    "event": "pressed" | "released",
    "key": key_index,
    "value": key_label
}
```

#### Dial Events

```python
{
    "type": "dial_event",
    "event": "turn" | "pressed" | "released",
    "dial": dial_index,
    "value": dial_value
}
```

#### Touchscreen Events

```python
{
    "type": "touchscreen_event",
    "event": "SHORT" | "LONG",
    "value": touch_value
}
```

## Advanced Features

### Dynamic Content Updates

#### Image Updates

```python
# Update key image via UDP
{
    "type": "update_label",
    "layer": 1,
    "target": "key",
    "index": 0,
    "label": "New Label",
    "image": "new_image.png"
}
```

#### Touchscreen Updates

```python
# Update touchscreen content
{
    "type": "update_label",
    "layer": 1,
    "target": "touchscreen",
    "touchscreen_data": {
        "lines": ["Line 1", "Line 2", "Line 3"]
    }
}
```

### Network Integration

#### External System Control

The UDP system allows integration with:
- Video switchers
- Audio consoles
- Lighting systems
- Automation systems
- Custom applications

#### Message Format

All messages use MessagePack serialization for efficiency:

```python
import msgpack

# Serialize message
encoded_data = msgpack.packb(data)

# Deserialize message
data = msgpack.unpackb(encoded_data, raw=False)
```

## Troubleshooting

### Common Issues

1. **Device Not Found**
   - Ensure Stream Deck is connected
   - Check USB connection
   - Verify device drivers

2. **Permission Errors**
   - Run with administrator privileges
   - Check device permissions
   - Ensure no other applications are using the device

3. **UDP Communication Issues**
   - Check network connectivity
   - Verify IP address and port settings
   - Check firewall settings
   - Ensure environment variables are set correctly

4. **Audio Control Problems**
   - Verify pycaw installation
   - Check Windows audio settings
   - Ensure audio device is available

5. **Configuration Issues**
   - Check environment variables are set correctly
   - Verify config.py file is accessible
   - Ensure network settings match your environment

### Debug Mode

Enable debug output by setting the DEBUG environment variable:

```bash
export DEBUG=true
python interactive.py
```

## Use Cases

### Live Production

- Camera switching
- Audio mixing
- Graphics insertion
- Lighting control

### Post-Production

- Timeline navigation
- Effect application
- Color grading
- Audio editing

### Broadcasting

- Studio automation
- Graphics management
- Audio routing
- Transmission control

## Contributing

1. Test with different Stream Deck models
2. Add support for additional protocols
3. Improve error handling
4. Add new preset configurations
5. Update configuration examples for new environments

## License

[Add your license information here]

## Support

For technical support:
- Check device compatibility
- Verify network settings
- Test UDP communication
- Review error messages
- Check configuration settings