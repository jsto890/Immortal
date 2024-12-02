import serial
import serial.tools.list_ports as port_list

def list_serial_ports():
    ports = list(port_list.comports())
    if not ports:
        print("No serial ports found.")
        return []
    for p in ports:
        print(p)
    return ports

def check_device_connection(port_name, baudrate=9600, timeout=1):
    try:
        with serial.Serial(port_name, baudrate=baudrate, timeout=timeout) as ser:
            if ser.is_open:
                print(f"Device connected on port {port_name}")
            else:
                print(f"No device connected on port {port_name}")
    except serial.SerialException as e:
        print(f"Error with serial port {port_name}: {e}")

def main():
    ports = list_serial_ports()
    if not ports:
        return

    for p in ports:
        check_device_connection(p.device)

if __name__ == "__main__":
    main()