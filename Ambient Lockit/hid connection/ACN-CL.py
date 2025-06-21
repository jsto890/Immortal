# First file to be run in the project
# Trying to connect laptop to ACN Lockit using USB HID connector

import hid
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import HID_VENDOR_ID, HID_PRODUCT_ID, CONFIG_NOTE

print(CONFIG_NOTE)

# Use config values instead of hardcoded IDs
VID = HID_VENDOR_ID
PID = HID_PRODUCT_ID

try :
    device = hid.device(vid = VID, pid = PID)
    print("Device found")
    
    while True:
        data = device.read(64)
        if data:
            print(f"Data read from device: {data}")
        else:
            print("Cant read data")       

except Exception as e:
    print(f"Error: {e}")
finally:
    device.close()
    print("Device closed")
    