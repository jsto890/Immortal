import hid
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HID_VENDOR_ID, HID_PRODUCT_ID, CONFIG_NOTE

print(CONFIG_NOTE)

try:
    device = hid.device(HID_VENDOR_ID, HID_PRODUCT_ID)
    print("Device found")
except Exception as e:
    print(f"Error to open: {e}")
    print(f"Tried to connect to VID: 0x{HID_VENDOR_ID:04X}, PID: 0x{HID_PRODUCT_ID:04X}")
    print("Please check your device connection and update config.py if needed")
    device = None
    
if device:
    try:
        data = device.read(64)
        print(f"Data read from device: {data}")
    except Exception as e:  
        print(f"Error during comms: {e}")
        
    finally:
        device.close()
        print("Device closed")