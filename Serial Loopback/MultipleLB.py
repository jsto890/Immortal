import serial
import serial.tools.list_ports as port_list
import time

# Could get rid of it only got one serial port
def list_serial_ports():
    ports = list(port_list.comports())
    if not ports:
        print("No serial ports found.")
        return []
    for p in ports:
        print(p)
    return ports

# Might need to adjust baudrate and timeout
def perform_loopback_test(port_name, baudrate=9600, timeout=1):
    try:
        with serial.Serial(port_name, baudrate=baudrate, timeout=timeout) as ser:
            test_data = b'Hello, RS232/RS485!'
            ser.write(test_data)
            time.sleep(1)
            received_data = ser.read(len(test_data))
            if received_data == test_data:
                print(f"Loopback test passed on port {port_name}")
            else:
                print(f"Loopback test failed on port {port_name}")
                print(f"Sent: {test_data}")
                print(f"Received: {received_data}")
    except serial.SerialException as e:
        print(f"Error with serial port {port_name}: {e}")

def main():
    ports = list_serial_ports()
    if not ports:
        return

    for p in ports:
        perform_loopback_test(p.device)

if __name__ == "__main__":
    main()