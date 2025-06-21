"""
Configuration file for Immortal project.
This file contains all configurable parameters that can be overridden with environment variables.
"""

import os

# Network Configuration
# These can be overridden with environment variables
UDP_IP = os.getenv('UDP_IP', '127.0.0.1')  # Default to localhost
UDP_PORT = int(os.getenv('UDP_PORT', '41234'))  # Default UDP send port
RECEIVE_PORT = int(os.getenv('RECEIVE_PORT', '41235'))  # Default UDP receive port

# HID Device Configuration
# These are example values - adjust for your specific devices
HID_VENDOR_ID = int(os.getenv('HID_VENDOR_ID', '0x10E6'), 16)  # Example vendor ID
HID_PRODUCT_ID = int(os.getenv('HID_PRODUCT_ID', '0x108C'), 16)  # Example product ID

# Serial Port Configuration
DEFAULT_BAUDRATE = int(os.getenv('DEFAULT_BAUDRATE', '9600'))
DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '1'))

# Stream Deck Configuration
ASSETS_PATH = os.getenv('ASSETS_PATH', 'Assets')
FONT_PATH = os.getenv('FONT_PATH', '/usr/share/fonts/ttf/LiberationSans-Regular.ttf')
TOUCHSCREEN_WIDTH = int(os.getenv('TOUCHSCREEN_WIDTH', '800'))
TOUCHSCREEN_HEIGHT = int(os.getenv('TOUCHSCREEN_HEIGHT', '100'))

# Development/Testing Configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Important Note for users
CONFIG_NOTE = """
IMPORTANT: This project was developed during a summer internship. 
Some configurations, IP addresses, and device identifiers may be specific 
to the development environment and should be adjusted for your use case.

To customize these settings:
1. Set environment variables (recommended)
2. Modify this config.py file directly
3. Use command line arguments in individual scripts
""" 