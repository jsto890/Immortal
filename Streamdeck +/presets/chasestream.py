import io
import os
import threading
import socket
import msgpack
import sys
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import UDP_IP, UDP_PORT, RECEIVE_PORT, CONFIG_NOTE

print(CONFIG_NOTE)

# Folder containing image assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
FONT_PATH = "/usr/share/fonts/ttf/LiberationSans-Bold.ttf"  # Use any TTF font available

exit_event = threading.Event()  # Global event to signal exit

# Key configuration
# Each key will have a label and multiple states (for toggles or cycles)
# We'll store the current state in separate variables.
# Keys (0-based index):
# 0: Points of Interest (toggle)
# 1: Speedometer (toggle)
# 2: Map (toggle)
# 3: News Ticker (toggle)
# 4: Street Names (toggle)
# 5: Map Position (cycle through list)
# 6: StreamDeck Power (toggle)
# 7: Exit (just exits)

global_key_labels = [
    "Points of Interest",
    "Speedometer",
    "Map",
    "News Ticker",
    "Street names",
    "Map Position",
    "Power",
    "Exit"
]

poi_on = False
speedometer_on = False
map_on = False
ticker_on = False
street_names_on = False
map_positions = ["Left Top", "Top Middle", "Right Top", "Right Middle", "Right Bottom", "Bottom Middle", "Left Bottom", "Left Middle"]
map_position_index = 0
power_on = False

# Dials
# 0: Breadcrumbs: press toggles on/off, turn sets minutes
breadcrumbs_on = False
breadcrumbs_minutes = 0

# 1: Brightness: press toggles dark/light, turn sets brightness magnitude
dark_mode = False
brightness_level = 50  # 0-100

# 2: Volume: press mute/unmute, turn sets volume percentage
mute_on = False
volume_level = 50  # 0-100

# 3: Zoom: press toggles zoom on/off, turn in/out
zoom_on = False
zoom_level = 100  # 100 = normal, >100 zoom in, <100 zoom out

global_key_images = [
    "image_1.png",
    "image_1.png",
    "image_1.png",
    "image_1.png",
    "image_1.png",
    "image_1.png",
    "image_1.png",
    "image_1.png"
]

global_dial_labels = ["Volume", "Zoom", "Brightness", "Not Set"]

def udp_listener():
    """Listen for incoming messages to update keys, dials, touchscreen from another code."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", RECEIVE_PORT))  # Python listens on this port
    while True:
        msg, addr = udp_socket.recvfrom(4096)
        try:
            data = msgpack.unpackb(msg, raw=False)
            process_udp_message(data)
        except Exception as e:
            print(f"Error processing message: {e}")

def process_udp_message(data):
    """Process incoming UDP messages to update labels."""
    global global_dial_labels, global_key_labels, global_key_images

    if data.get("type") == "update_label":
        target = data.get("target")
        index = data.get("index")
        label = data.get("label")
        simage = data.get("image")

        if target == "dial" and 0 <= index < len(global_dial_labels):
            global_dial_labels[index] = str(label)
            print(f"Updated dial {index} to label '{label}'")
            # Refresh the touchscreen or key labels
            update_touchscreen_image(deck)
        elif target == "key" and 0 <= index < len(global_key_labels):
            global_key_labels[index] = str(label)
            global_key_images[index] = str(simage)
            print(f"Updated key {index} to label '{label}'")
            update_key_image(deck, index, False)  # Refresh the key image
        else:
            print(f"Invalid target or index: {target}, {index}")


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

def set_touchscreen_image(deck, image_path):
    global global_dial_labels
    # Open the image file
    tscreen = Image.open(image_path)

    # Convert the image to RGB mode if it's not already
    if tscreen.mode != 'RGB':
        tscreen = tscreen.convert('RGB')
    
    tscreenl = create_touchscreen_image(tscreen, global_dial_labels)
    
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
    
    global global_key_labels, global_key_images

    # Get key style for the specified key
    if key < len(global_key_labels):
        return {
            "icon": os.path.join(ASSETS_PATH, global_key_images[key]),  # Use the specified icon
            "font": FONT_PATH,
            "label": global_key_labels[key]
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
    global global_dial_labels

    """Callback for dial turn and press events."""
    if event == DialEventType.TURN:
        print(f"Dial {dial} turned with value {value}.")
        data = {
            "type": "dial_event",
            "event": "turn",
            "label": global_dial_labels[dial],
            "dial": dial,
            "value": value
        }
    elif event == DialEventType.PUSH:
        print(f"Dial {dial} {'pressed' if value == 1 else 'released'}.")
        data = {
            "type": "dial_event",
            "event": "pressed" if value == 1 else "released",
            "label": global_dial_labels[dial],
            "dial": dial,
            "value": value
        }
    send_udp_message(data)  # Send the event data over UDP

def touchscreen_event_callback(deck, event, value):
    global global_dial_labels
    """Callback for touchscreen press events."""
    x = value.get("x", None)
    
    if x is not None:
        if 0 <= x < 200:
            print(f"Touchscreen event: {event}, label: {global_dial_labels[0]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_dial_labels[0],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP
        elif 200 <= x < 400:
            print(f"Touchscreen event: {event}, label: {global_dial_labels[1]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_dial_labels[1],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP
        elif 400 <= x < 600:
            print(f"Touchscreen event: {event}, label: {global_dial_labels[2]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_dial_labels[2],	
                "value": value
            }
            send_udp_message(data)  # Send the event data over UDP
        elif 600 <= x < 800:
            print(f"Touchscreen event: {event}, label: {global_dial_labels[3]}, value: {value}.")
            data = {
                "type": "touchscreen_event",
                "event": event.name,  # Convert Enum to string
                "label": global_dial_labels[3],	
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
            