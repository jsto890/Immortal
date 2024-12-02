# First file to be run in the project
# Trying to connect laptop to ACN Lockit using USB HID connector

import hidpy as hid

VID = 0x10E6
PID = 0x108C

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
    