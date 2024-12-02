import serial
import time

def perform_loopback_test(port_name, baudrate, timeout):
    try:
        with serial.Serial(port_name, baudrate=baudrate, timeout=timeout) as ser:
            test_data = b'Hello'
            ser.write(test_data)
            time.sleep(1)
            received_data = ser.read(len(test_data))
            if received_data == test_data:
                print(f"Loopback test passed on port {port_name}")
                print(f"Sent: {test_data}")
                print(f"Received: {received_data}")
            else:
                print(f"Loopback test failed on port {port_name}")
                print(f"Sent: {test_data}")
                print(f"Received: {received_data}")
    except serial.SerialException as e:
        print(f"Error with serial port {port_name}: {e}")

def main():
    port_name = "COM4"  # Replace with the actual port name
    baudrate = 115200 # Might need to adjust baudrate
    timeout = 1 # Might need to adjust timeout
    perform_loopback_test(port_name, baudrate, timeout)

if __name__ == "__main__":
    main()