import io
import os
import threading
import sys
import socket
import msgpack
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

UDP_IP = "192.168.1.200"
UDP_PORT = 41234

# Folder containing image assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
FONT_PATH = "/usr/share/fonts/ttf/LiberationSans-Bold.ttf"  # Use any TTF font available

exit_event = threading.Event()  # Global event to signal exit

def udp_listener():
    """Listen for incoming messages from the JavaScript server."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", 41235))  # Python listens on this port
    while True:
        msg, addr = udp_socket.recvfrom(1024)
        try:
            data = msgpack.unpackb(msg)
            process_udp_message(data)
        except Exception as e:
            print(f"Error processing message: {e}")

def process_udp_message(data):
    """Process incoming UDP messages to update labels."""
    global global_labels

    if data.get("type") == "update_label":
        target = data.get("target")
        index = data.get("index")
        label = data.get("label")

        if target == "dial" and 0 <= index < len(global_labels):
            global_labels[index] = label
            print(f"Updated dial {index} to label '{label}'")
        elif target == "key":
            # Logic to update button labels if needed
            print(f"Updated key {index} to label '{label}'")
        else:
            print(f"Invalid target or index: {target}, {index}")

        # Refresh the touchscreen or button labels
        update_touchscreen_image(deck)

def send_udp_message(data):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    encoded_data = msgpack.packb(data)
    udp_socket.sendto(encoded_data, (UDP_IP, UDP_PORT))
    udp_socket.close()

def create_touchscreen_image(image, labels):
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except (OSError, IOError):
        print(f"Failed to load font '{FONT_PATH}'. Falling back to default font.")
        font = ImageFont.load_default()

    # Define positions for the labels above each dial
    dial_positions = [100, 415, 730, 1060]  # Approximate x-coordinates for the 4 dials
    for i, label in enumerate(labels):
        # Use textbbox if available, fallback to approximate placement
        if hasattr(draw, "textbbox"):
            text_bbox = draw.textbbox((0, 0), label, font=font)  # Calculate text dimensions
            text_width = text_bbox[2] - text_bbox[0]
        else:
            text_width, _ = draw.textsize(label, font=font)

        text_position = (dial_positions[i] - text_width // 2, 175)  # Centered above each dial
        draw.text(text_position, label, font=font, fill="white")  # Draw the text

    return image

global_labels = []

def set_touchscreen_image(deck, image_path):
    global global_labels
    # Open the image file
    tscreen = Image.open(image_path)

    # Convert the image to RGB mode if it's not already
    if tscreen.mode != 'RGB':
        tscreen = tscreen.convert('RGB')

    labels = ["Volume", "Zoom", "Brightness", "Not Set"]
    global_labels = labels
    
    tscreenl = create_touchscreen_image(tscreen, labels)
    
    # Resize the image to fit the Stream Deck touchscreen
    image = tscreenl.resize((800, 100), Image.LANCZOS)

    # Convert the image to the native format of the Stream Deck touchscreen
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    native_image = img_byte_arr.getvalue()

    # Set the image on the touchscreen
    deck.set_touchscreen_image(native_image, 0, 0, 800, 100)
    
def update_touchscreen_image(deck):
    image_path = os.path.join(ASSETS_PATH, "wide.jpeg")
    set_touchscreen_image(deck, image_path)

# Existing functions for keys remain unchanged
def render_key_image(deck, icon_filename, font_filename, label_text):
    """Generate an image with an icon and text below it for a Stream Deck key."""
    # Resize the icon to fit with space for text
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_key_image(deck, icon, margins=[-30, -20, 0, -20])

    # Draw text onto the image
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font_filename, 14)
    except (OSError, IOError):
        print(f"Failed to load font '{font_filename}'. Falling back to default font.")
        font = ImageFont.load_default()

    # Use textbbox to calculate text dimensions
    text_bbox = draw.textbbox((0, 0), label_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Center the text at the bottom of the key
    text_position = ((image.width - text_width) // 2, image.height - text_height - 11.5)
    draw.text(text_position, label_text, font=font, fill="white")

    return PILHelper.to_native_key_format(deck, image)

def get_key_style(deck, key, state):
    """Define the style for each key, including icon and text."""
    exit_key_index = deck.key_count() - 1

    key_styles = [
        {"icon": "image_1.png", "label": "Camera On"},
        {"icon": "image_1.png", "label": "Camera Off"},
        {"icon": "image_1.png", "label": "Stabilise"},
        {"icon": "image_1.png", "label": "Map"},
        {"icon": "image_1.png", "label": "Speed"},
        {"icon": "image_1.png", "label": "Lighting"},
        {"icon": "image_1.png", "label": "Channel"},
        {"icon": "image_1.png", "label": "Exit"},
    ]

    # Get key style for the specified key
    if key < len(key_styles):
        return {
            "icon": os.path.join(ASSETS_PATH, key_styles[key]["icon"]),
            "font": FONT_PATH,
            "label": key_styles[key]["label"]
        }
    else:
        return {
            "icon": os.path.join(ASSETS_PATH, "default.png"),  # Default fallback
            "font": FONT_PATH,
            "label": f"Key {key + 1}"
        }

def update_key_image(deck, key, state):
    """Update the key with its icon and text."""
    key_style = get_key_style(deck, key, state)
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    with deck:
        deck.set_key_image(key, image)

def key_change_callback(deck, key, state):
    """Callback for key press events."""
    print(f"Key {key} {'pressed' if state else 'released'} on deck {deck.id()}.")
    
    label = get_key_style(deck, key, state)["label"]  # Get the label for the key

    data = {
        "type": "key_event",
        "event": "pressed" if state else "released",
        "key": key,
        "value": label
    }
    send_udp_message(data)  # Send the event data over UDP
    
    if state:
        # Update the key image dynamically based on state
        update_key_image(deck, key, state)

        # Exit the program if the last key is pressed
        if key == deck.key_count() - 1:
            print("Exit key pressed.")
            with deck:
                deck.reset()
            exit_event.set()

def dial_change_callback(deck, dial, event, value):
    global global_labels

    """Callback for dial turn and press events."""
    if event == DialEventType.TURN:
        print(f"Dial {dial} turned with value {value}.")
        data = {
            "type": "dial_event",
            "event": "turn",
            "label": global_labels[dial],
            "dial": dial,
            "value": value
        }
    elif event == DialEventType.PUSH:
        print(f"Dial {dial} {'pressed' if value == 1 else 'released'}.")
        data = {
            "type": "dial_event",
            "event": "pressed" if value == 1 else "released",
            "label": global_labels[dial],
            "dial": dial,
            "value": value
        }
    send_udp_message(data)  # Send the event data over UDP

def touchscreen_event_callback(deck, event, value):
    global global_labels
    """Callback for touchscreen press events."""
    x = value.get("x", None)
    
    if x is not None:
        if 0 <= x < 200:
            print(f"Touchscreen event: {event}, label: {global_labels[0]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_labels[0],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP
        elif 200 <= x < 400:
            print(f"Touchscreen event: {event}, label: {global_labels[1]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_labels[1],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP
        elif 400 <= x < 600:
            print(f"Touchscreen event: {event}, label: {global_labels[2]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_labels[2],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP
        elif 600 <= x < 800:
            print(f"Touchscreen event: {event}, label: {global_labels[3]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_labels[3],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()
    print(f"Found {len(streamdecks)} Stream Deck(s).")

    for deck in streamdecks:
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print(f"Opened '{deck.deck_type()}' device (serial number: {deck.get_serial_number()}")

        # Set brightness
        deck.set_brightness(50)

        # Initialize keys with icons and labels
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register event callbacks
        deck.set_key_callback(key_change_callback)
        deck.set_dial_callback(dial_change_callback)
        deck.set_touchscreen_callback(touchscreen_event_callback)
        update_touchscreen_image(deck)
        
        # Start UDP listener thread
        udp_thread = threading.Thread(target=udp_listener, daemon=True)
        udp_thread.start()

        # Keep the script running
        print("Listening for events. Press Ctrl+C to exit.")
        try:
            while not exit_event.is_set():
                exit_event.wait(0.1)  # Wait briefly to allow handling of KeyboardInterrupt
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting...")
            exit_event.set()

        # Reset the deck and close the connection
        with deck:
            deck.reset()
            deck.close()
            