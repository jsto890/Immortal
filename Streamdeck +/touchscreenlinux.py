import io
import os
import threading
import sys
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

# Folder containing image assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
FONT_PATH = "/usr/share/fonts/ttf/LiberationSans-Regular.ttf"  # Use any TTF font available

exit_event = threading.Event()  # Global event to signal exit

def create_touchscreen_image(deck, labels):
    """Generate an image for the touchscreen with labels above each dial."""
    background_path = os.path.join(ASSETS_PATH, "background.jpg")
    if not os.path.exists(background_path):
        raise FileNotFoundError(f"Background image not found at {background_path}")

    image = Image.open(background_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(FONT_PATH, 20)
    except (OSError, IOError):
        print(f"Failed to load font '{FONT_PATH}'. Falling back to default font.")
        font = ImageFont.load_default()

    # Define positions for the labels above each dial
    dial_positions = [80, 310, 510, 750]  # Approximate x-coordinates for the 4 dials
    for i, label in enumerate(labels):
        # Use textbbox if available, fallback to approximate placement
        if hasattr(draw, "textbbox"):
            text_bbox = draw.textbbox((0, 0), label, font=font)  # Calculate text dimensions
            text_width = text_bbox[2] - text_bbox[0]
        else:
            text_width, _ = draw.textsize(label, font=font)

        text_position = (dial_positions[i] - text_width // 2, 10)  # Centered above each dial
        draw.text(text_position, label, font=font, fill="white")  # Draw the text

    return image

def set_touchscreen_labels(deck):
    """Set the touchscreen image with labels for the dials."""
    labels = ["Volume", "Zoom", "Brightness", "Not Set"]
    image = create_touchscreen_image(deck, labels)

    image = image.resize((800, 100), Image.LANCZOS)
    print(f"Setting touchscreen image with size {image.size}")

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    native_image = img_byte_arr.getvalue()

    try:
        deck.set_touchscreen_image(native_image, 0, 0, 800, 100)
        print("Touchscreen image set successfully.")
    except Exception as e:
        print(f"Failed to set touchscreen image: {e}")

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
    text_position = ((image.width - text_width) // 2, image.height - text_height - 10)
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
    """Callback for dial turn and press events."""
    if event == DialEventType.TURN:
        print(f"Dial {dial} turned with value {value}.")
    elif event == DialEventType.PUSH:
        print(f"Dial {dial} {'pressed' if value == 1 else 'released'}.")

def touchscreen_event_callback(deck, event, value):
    """Callback for touchscreen press events."""
    print(f"Touchscreen event: {event}, value: {value}.")

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

        # Set touchscreen labels
        set_touchscreen_labels(deck)

        # Initialize keys with icons and labels
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register event callbacks
        deck.set_key_callback(key_change_callback)
        deck.set_dial_callback(dial_change_callback)
        deck.set_touchscreen_callback(touchscreen_event_callback)

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
            