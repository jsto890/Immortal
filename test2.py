import hid

try:
    device = hid.device(0x10E6, 0x108C)
    print("Device found")
except Exception as e:
    print(f"Error to open: {e}")
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