import io
import os
import threading
import socket
import msgpack
import requests
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import UDP_IP, UDP_PORT, RECEIVE_PORT, CONFIG_NOTE

print(CONFIG_NOTE)

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
FONT_PATH = "/usr/share/fonts/ttf/LiberationSans-Bold.ttf"

exit_event = threading.Event()

# Current layer of the interface. Starts at 1
current_layer = 1

# Data structures for keys, dials, touchscreen
# keys_data[layer][key] = {"label": str, "image": str}
keys_data = {1: {}, 2: {}, 3: {}}

# dial_data[layer][dial] = {"label": str, "value": ...} - can store relevant info
dial_data = {1: {}, 2: {}, 3: {}}

# touchscreen_data[layer] = {"lines": [...], ...} - store whatever textual info is needed
touchscreen_data = {1: {}, 2: {}, 3: {}}

# Default fallback image if none provided
DEFAULT_IMAGE = "image_1.png"

# Touchscreen background image (constant)
TOUCHSCREEN_BG = "wide.jpeg"

POWER_ON = "power_on.png"

MODE = "mode.png"

EXIT = "exit1.png"

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

def udp_listener():
    """Listen for incoming messages to update keys, dials, touchscreen from another code."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", RECEIVE_PORT))
    while True:
        msg, addr = udp_socket.recvfrom(4096)
        try:
            data = msgpack.unpackb(msg, raw=False)
            process_udp_message(data)
        except Exception as e:
            print(f"Error processing message: {e}")

def process_udp_message(data):
    # Expected data format could be:
    # {"type": "update_label", "layer": int, "target": "key"/"dial"/"touchscreen", "index": int, "label": str, "image": str}
    # This is an example. Adjust according to your actual message format.
    msg_type = data.get("type")

    if msg_type == "update_label":
        layer = data.get("layer")
        target = data.get("target")
        index = data.get("index")
        label = data.get("label", "")
        image = data.get("image", "")

        if layer not in (1, 2, 3):
            return  # Invalid layer, ignore

        if target == "key":
            # Store the data for that key in the specified layer
            keys_data[layer][index] = {"label": label, "image": image}
            # If we are currently on that layer, update the key image
            if current_layer == layer:
                update_key_image(deck, index)

        elif target == "dial":
            # Store dial data
            dial_data[layer][index] = {"label": label}  # Add more fields if needed
            # If current layer matches, update touchscreen to reflect changes
            if current_layer == layer:
                update_touchscreen_image(deck)

        elif target == "touchscreen":
            # Could be multiple lines or just a label
            # For simplicity, store a dict of data. Could be {"lines": [...]} or just a "label"
            touchscreen_data[layer] = data.get("touchscreen_data", {})
            if current_layer == layer:
                update_touchscreen_image(deck)
                
    elif msg_type == "update_image_link":
        image_url = data.get("image_url")
        filename = data.get("filename", "received_image.png")
        if image_url:
            print(f"Received image link: {image_url}")
            try:
                download_image(image_url, filename)
            except Exception as e:
                print(f"Error downloading image: {e}")
        else:
            print("No image_url provided in the message.")

    # Add other message types as needed.

def send_udp_message(data):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    encoded_data = msgpack.packb(data)
    udp_socket.sendto(encoded_data, (UDP_IP, UDP_PORT))
    udp_socket.close()

def create_touchscreen_image(deck, layer):
    # Create an image for the touchscreen using data from touchscreen_data[layer]
    # Start with background image
    tscreen = Image.open(os.path.join(ASSETS_PATH, TOUCHSCREEN_BG))
    if tscreen.mode != 'RGB':
        tscreen = tscreen.convert('RGB')
    draw = ImageDraw.Draw(tscreen)
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except:
        font = ImageFont.load_default()

    # touchscreen_data[layer] might have lines to display or other info
    # For example, if we have {"lines": ["Line1", "Line2"]}, we display them.
    tdata = touchscreen_data.get(layer, {})
    lines = tdata.get("lines", [])
    # Print lines centered
    y_offset = 10
    for line in lines:
        if hasattr(draw, "textbbox"):
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        else:
            text_width, text_height = draw.textsize(line, font=font)
        x_pos = (tscreen.width - text_width) // 2
        draw.text((x_pos, y_offset), line, font=font, fill="white")
        y_offset += text_height + 5

    # Also, we might want to display dial info from dial_data[layer]
    # For example: dial_data[layer][0]["label"] etc.
    # This is an example; adjust formatting as needed.
    # We'll just print dial labels in a row if present.
    dial_labels = [dial_data[layer].get(i, {}).get("label", "") for i in range(4)]
    y_bottom = tscreen.height - 200  # move text ~50px above the bottom of the original image
    x_coords = [120, 410, 750, 1060] # approximate positions for 4 dials

    for i, dlbl in enumerate(dial_labels):
        if dlbl:
            if hasattr(draw, "textbbox"):
                tb = draw.textbbox((0,0), dlbl, font=font)
                dw = tb[2] - tb[0]
            else:
                dw, dh = draw.textsize(dlbl, font=font)
            # Place each dial label at x_coords[i], centered horizontally
            x_pos = x_coords[i] - dw//2
            draw.text((x_pos, y_bottom), dlbl, font=font, fill="white")

    # Resize image to touchscreen dimensions if needed (assume 800x100)
    image = tscreen.resize((800, 150), Image.LANCZOS)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    native_image = img_byte_arr.getvalue()
    return native_image

def update_touchscreen_image(deck):
    native_image = create_touchscreen_image(deck, current_layer)
    deck.set_touchscreen_image(native_image, 0, 0, 800, 100)

def get_key_image_and_label(layer, key):
    kdata = keys_data.get(layer, {}).get(key, {})
    label = kdata.get("label", "")
    image = kdata.get("image", DEFAULT_IMAGE)

    # Handle special keys with fallback logic if no UDP data was given
    if layer == 1:
        # Layer 1: Only key 7 is "Power On"
        if key == 7 and not kdata:  # no data provided
            image = POWER_ON
            label = "Power On"

    elif layer == 2:
        # Layer 2: key 7 = Exit, key 3 = Mode
        if key == 7 and not kdata:
            image = EXIT
            label = "Exit"
        if key == 3 and not kdata:
            image = MODE
            label = "Mode"

    elif layer == 3:
        # Layer 3: key 7 = Exit, key 3 = Mode
        if key == 7 and not kdata:
            image = EXIT
            label = "Exit"
        if key == 3 and not kdata:
            image = MODE
            label = "Mode"

    return label, image

def render_key_image(deck, icon_filename, font_filename, label_text, key, is_pressed=False):
    global current_layer
    icon_path = os.path.join(ASSETS_PATH, icon_filename)
    if not os.path.exists(icon_path):
        # If image not found, use a blank default image you have
        icon_path = os.path.join(ASSETS_PATH, DEFAULT_IMAGE)
    
    # 1. Open the source image
    icon = Image.open(icon_path).convert("RGBA")

    # 2. Determine the final size for each key
    key_width, key_height = deck.key_image_format()["size"]  # Typically (100, 100)

    # 3. Crop & scale the icon to exactly (key_width, key_height - 35) for the image portion
    icon = ImageOps.fit(icon, (key_width, key_height - 35), Image.LANCZOS)

    # 4. Create a blank key image canvas
    image = PILHelper.create_key_image(deck)

    # 5. Paste the scaled icon at (0, 0)
    image.paste(icon, (0, 0))
    
    draw = ImageDraw.Draw(image)
    green_bar_height = 35
    
    label = label_text
    
    text_color = "white"

    # If we're on layer 2, toggle label from "X On" to "X Off"
    if current_layer in [2, 3] and key not in [3, 7]:
        if label.endswith("On"):
            draw.rectangle(
                [(0, key_height - green_bar_height), (key_width, key_height)],
                fill=(0, 255, 0)
            )
            text_color = "black"
        elif label.endswith("Off"):
            draw.rectangle(
                [(0, key_height - green_bar_height), (key_width, key_height)],
                fill=(0, 0, 0)
            )
            text_color = "white"

    if label_text:
        # 7. Draw label text
        try:
            font = ImageFont.truetype(font_filename, 14)
        except (OSError, IOError):
            font = ImageFont.load_default()

        if hasattr(draw, "textbbox"):
            text_bbox = draw.textbbox((0, 0), label_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        else:
            text_width, text_height = draw.textsize(label_text, font=font)

        # Center label within the green bar
        x_pos = (key_width - text_width) // 2
        y_pos = key_height - green_bar_height + (green_bar_height - text_height) // 2
        draw.text((x_pos, y_pos), label_text, font=font, fill=text_color)

    # 8. Convert the PIL image to Stream Deck's native format
    return PILHelper.to_native_key_format(deck, image)


def update_key_image(deck, key, is_pressed=False):
    label, img = get_key_image_and_label(current_layer, key)
    image = render_key_image(deck, img, FONT_PATH, label, key, is_pressed)
    with deck:
        deck.set_key_image(key, image)

def refresh_all_keys(deck):
    # Only show relevant keys for the current layer
    # Actually all keys can be updated, but only some keys have meaningful data
    # The instructions don't say to hide keys, just that some keys have functions.
    # We'll update all keys with whatever data is available for the current layer.
    for k in range(deck.key_count()):
        update_key_image(deck, k)

def send_event_message(event_type, detail):
    # event_type: "key_event", "dial_event", "touchscreen_event"
    # detail: dict with info about the event
    # Add current layer info
    detail["layer"] = current_layer
    send_udp_message(detail)

def key_change_callback(deck, key, state):
    global current_layer
    if state:
        print(f"Key {key} pressed at layer {current_layer}.")

        label, img = get_key_image_and_label(current_layer, key)

        # Default new_label to existing label so it's always defined
        new_label = label

        # If we're on layer 2, toggle label from "X On" to "X Off"
        if current_layer in [2, 3] and key not in [3, 7]:
            if label.endswith("On"):
                new_label = label[:-2] + "Off"
            elif label.endswith("Off"):
                new_label = label[:-3] + "On"
            else:
                new_label = label + " On"

            keys_data[current_layer][key] = {"label": new_label, "image": img}
            update_key_image(deck, key)

        # Now new_label is always defined, we can safely reference it
        send_event = {
            "type": "key_event",
            "event": "pressed",
            "key": key,
            "value": new_label
        }
        send_event_message("key_event", send_event)

        # The rest of your layer-switch logic
        if current_layer == 1:
            if key == 7:
                current_layer = 2
                refresh_all_keys(deck)
                update_touchscreen_image(deck)
        elif current_layer == 2:
            if key == 7:
                with deck:
                    deck.reset()
                exit_event.set()
            elif key == 3:
                current_layer = 3
                refresh_all_keys(deck)
                update_touchscreen_image(deck)
        elif current_layer == 3:
            if key == 7:
                with deck:
                    deck.reset()
                exit_event.set()
            elif key == 3:
                current_layer = 2
                refresh_all_keys(deck)
                update_touchscreen_image(deck)

def dial_change_callback(deck, dial, event, value):
    # Dials are general, updated via UDP. Just send events with layer info.
    if event == DialEventType.TURN:
        # Adjust dial states if needed. Values from UDP define what they mean.
        # Just send event out.
        send_event = {
            "type": "dial_event",
            "event": "turn",
            "dial": dial,
            "value": value
        }
        send_event_message("dial_event", send_event)
        update_touchscreen_image(deck)

    elif event == DialEventType.PUSH:
        # Toggles on press down if needed. This depends on UDP logic.
        # We'll assume the UDP logic defines what pushing a dial does.
        if value == 1:
            # Press down
            # You could toggle a state in dial_data if required.
            pass

        send_event = {
            "type": "dial_event",
            "event": "pressed" if value == 1 else "released",
            "dial": dial,
            "value": value
        }
        send_event_message("dial_event", send_event)
        update_touchscreen_image(deck)

def touchscreen_event_callback(deck, event, value):
    # If touchscreen is touched, send event with layer info
    send_event = {
        "type": "touchscreen_event",
        "event": event.name,
        "value": value
    }
    send_event_message("touchscreen_event", send_event)

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()
    print(f"Found {len(streamdecks)} Stream Deck(s).")

    for deck in streamdecks:
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print(f"Opened '{deck.deck_type()}' device (serial number: {deck.get_serial_number()}")

        deck.set_brightness(50)

        # Initially in layer 1
        refresh_all_keys(deck)
        update_touchscreen_image(deck)

        deck.set_key_callback(key_change_callback)
        deck.set_dial_callback(dial_change_callback)
        deck.set_touchscreen_callback(touchscreen_event_callback)

        # Start UDP listener thread
        udp_thread = threading.Thread(target=udp_listener, daemon=True)
        udp_thread.start()

        print("Listening for events. Press Ctrl+C to exit.")
        try:
            while not exit_event.is_set():
                exit_event.wait(0.1)
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting...")
            exit_event.set()

        with deck:
            deck.reset()
            deck.close()