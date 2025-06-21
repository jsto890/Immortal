import os
import socket
import msgpack
import requests
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import RECEIVE_PORT, CONFIG_NOTE

print(CONFIG_NOTE)

# Configuration
UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = RECEIVE_PORT

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
if not os.path.exists(ASSETS_PATH):
    os.makedirs(ASSETS_PATH)

def download_image(image_url, filename):
    # Download the image from the provided URL
    response = requests.get(image_url, stream=True)
    response.raise_for_status()  # Raise an error if not successful

    # Save the image to the Assets directory
    filepath = os.path.join(ASSETS_PATH, filename)
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Image saved to {filepath}")

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}:{UDP_PORT}")

    while True:
        msg, addr = sock.recvfrom(4096)
        try:
            data = msgpack.unpackb(msg, raw=False)
            msg_type = data.get("type")
            if msg_type == "update_image_link":
                image_url = data.get("image_url")
                filename = data.get("filename", "received_image.png")

                if image_url:
                    print(f"Received image link from {addr}: {image_url}")
                    download_image(image_url, filename)
                else:
                    print("No image_url provided in the message.")
            else:
                print(f"Received unknown message type '{msg_type}' from {addr}: {data}")

        except Exception as e:
            print(f"Error processing message from {addr}: {e}")

if __name__ == "__main__":
    start_server()
