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

global_key_labels = [
    "Camera On",
    "Camera Off",
    "Stabilise",
    "Map",
    "Speed",
    "Lighting",
    "Channel",
    "Exit"
]

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

global_dial_labels = [
    "Volume", 
    "Zoom", 
    "Brightness", 
    "Not Set"
]

def udp_listener(port, handler):
    """General-purpose UDP listener."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", port))
    print(f"Listening on port {port}")

    while True:
        try:
            msg, addr = udp_socket.recvfrom(65507)
            print(f"Received data on port {port} from {addr}: {msg[:50]}")  # Log first 50 bytes of the message
            if b"END" in msg:  # Handle end marker for image data
                continue
            handler(msg, addr)  # Delegate handling to the specified function
        except Exception as e:
            print(f"Error receiving message on port {port}: {e}")

def handle_label_update(msg, addr, deck):
    """Process label update messages."""
    try:
        data = msgpack.unpackb(msg, strict_map_key=False)
        process_udp_message(data, deck)
    except msgpack.exceptions.ExtraData as e:
        print(f"Error: Extra data in message - {e}")
    except msgpack.exceptions.UnpackValueError as e:
        print(f"Error: Invalid msgpack data - {e}")
    except Exception as e:
        print(f"Error processing label update: {e}")

def handle_image_data(msg, addr, deck):
    global image_buffer, image_label, global_key_labels

    print(f"Handling image data for label '{image_label}'")

    if msg == b"END":
        try:
            # Load the image directly from the buffer
            img = Image.open(io.BytesIO(image_buffer))
            img = img.convert("RGB")  # Ensure correct format
            
            if image_label in global_key_labels:
                data = msgpack.unpackb(msg, strict_map_key=False)
                label = data.get("label", "")
                image_label = label
                key_index = global_key_labels.index(image_label)
                print(f"Updating key {key_index} with image for label '{image_label}'")
                
                global_key_images[key_index] = f"{image_label}.png"  # Update the image path
                
                # Resize and render the image directly for the key
                deck_image = PILHelper.create_scaled_key_image(deck, img)
                with deck:
                    deck.set_key_image(key_index, PILHelper.to_native_key_format(deck, deck_image))

                print(f"Key {key_index} updated with new image directly.")
            else:
                print(f"Label '{image_label}' not found in global_key_labels. Cannot update key.")

        except Exception as e:
            print(f"Error processing image data: {e}")
        finally:
            image_buffer = b""  # Clear buffer for the next image
    else:
        image_buffer += msg

def process_udp_message(data, deck):
    global global_key_labels, global_key_images, global_dial_labels, image_label

    print(f"Processing message: {data}")

    if data.get("type") == "update_label":
        target = data.get("target", "")
        index = data.get("index", -1)
        label = data.get("label", "")

        print(f"Received update: target={target}, index={index}, label={label}")

        if target == "key" and 0 <= index < len(global_key_labels):
            global_key_labels[index] = label
            image_label = label  # Set label for the incoming image
            print(f"Updated key {index} to label '{label}'")
            update_key_image(deck, index, False)
        elif target == "dial" and 0 <= index < len(global_dial_labels):
            global_dial_labels[index] = label
            print(f"Updated dial {index} to label '{label}'")
            update_touchscreen_image(deck)
        else:
            print(f"Invalid update: {data}")


# Initialize image buffer and label
image_buffer = b""
image_label = ""

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

    if key < len(global_key_labels):
        icon_path = f"/home/root/STREAMDECK/py_files/Assets/{global_key_images[key]}"
        print(f"Key {key} style: Label = {global_key_labels[key]}, Icon = {icon_path}")
        return {
            "icon": icon_path,  # Use the updated path
            "font": FONT_PATH,
            "label": global_key_labels[key]
        }
    else:
        return {
            "icon": os.path.join(ASSETS_PATH, "image_1.png"),  # Default fallback
            "font": FONT_PATH,
            "label": f"Key {key + 1}"
        }

def update_key_image(deck, key, state):
    """Update the key with its icon and text."""
    key_style = get_key_style(deck, key, state)
    print(f"Attempting to update key {key}: Label = {key_style['label']}, Image = {key_style['icon']}")

    if not os.path.exists(key_style["icon"]):
        print(f"Image not found: {key_style['icon']}. Falling back to default.")
        key_style["icon"] = "/home/root/STREAMDECK/py_files/Assets/image_1.png"

    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])
    print(f"Image rendered for key {key}")

    with deck:
        deck.set_key_image(key, image)
        print(f"Key {key} updated successfully.")


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
        udp_thread = threading.Thread(
            target=udp_listener, args=(RECEIVE_PORT, lambda msg, addr: handle_label_update(msg, addr, deck)), daemon=True
        )
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
            