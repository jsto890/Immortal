import os
import io
import threading
import webbrowser

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

is_muted = False

# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_key_image(deck, icon, margins=[0, 0, 20, 0])

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_key_format(deck, image)

# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
    # Last button in the example application is the exit button.
    exit_key_index = deck.key_count() - 1

    if key == exit_key_index:
        name = "long"
        icon = "long.png"
        font = "AovelSansRounded-rdDL.ttf"
        label = "Bye" if state else "Exit"
    elif key == 0:
        name = "google"
        icon = "google.png"
        font = "AovelSansRounded-rdDL.ttf"
        label = "Google"
    elif key == 1:
        name = "mute"
        icon = "mute.png" if is_muted else "volume.png"
        font = "AovelSansRounded-rdDL.ttf"
        label = "Muted" if is_muted else "Unmuted"
    else:
        name = "immortal"
        icon = "immortal.png" if state else "whitesquare.jpg"
        font = "AovelSansRounded-rdDL.ttf"
        label = "Pressed!" if state else "Key {}".format(key + 1)

    return {
        "name": name,
        "icon": os.path.join(ASSETS_PATH, icon),
        "font": os.path.join(ASSETS_PATH, font),
        "label": label
    }


# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    global is_muted
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    # Don't try to draw an image on a touch button
    if key >= deck.key_count():
        return

    # Update the key image based on the new key state.
    update_key_image(deck, key, state)

    # Check if the key is changing to the pressed state.
    if state:
        key_style = get_key_style(deck, key, state)

        # When an exit button is pressed, close the application.
        if key_style["name"] == "exit":
            # Use a scoped-with on the deck to ensure we're the only thread
            # using it right now.
            with deck:
                # Reset deck, clearing all button images.
                deck.reset()

                # Close deck handle, terminating internal worker threads.
                deck.close()
    
        elif key == 0:
            webbrowser.open('https://www.google.com')
            
        elif key == 1:
            CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            is_muted = not is_muted
            volume.SetMute(is_muted, None)
            print(f"Muted: {is_muted}")
            
            update_key_image(deck, key, state)
            update_touchscreen_image(deck)
        
                
def set_touchscreen_image(deck, image_path):
    # Open the image file
    tscreen = Image.open(image_path)

    # Convert the image to RGB mode if it's not already
    if tscreen.mode != 'RGB':
        tscreen = tscreen.convert('RGB')

    # Resize the image to fit the Stream Deck touchscreen
    image = tscreen.resize((800, 100), Image.LANCZOS)

    # Convert the image to the native format of the Stream Deck touchscreen
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    native_image = img_byte_arr.getvalue()

    # Set the image on the touchscreen
    deck.set_touchscreen_image(native_image, 0, 0, 800, 100)
    
def update_touchscreen_image(deck):
    global is_muted
    image_path = os.path.join(ASSETS_PATH, "mute.png" if is_muted else "volume.png")
    set_touchscreen_image(deck, image_path)
    
def touchscreen_event_callback(deck, event, value):
    global is_muted
    if event == TouchscreenEventType.SHORT:
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        is_muted = not is_muted
        volume.SetMute(is_muted, None)
        print(f"Muted: {is_muted}")
        update_touchscreen_image(deck)
        update_key_image(deck, 1, True)
    
def dial_change_callback(deck, dial, event, value):
    if event == DialEventType.TURN:
        print(f"Dial {dial} turned: {value}")
        if dial == 1:
            CoInitialize()
            #adjust volume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, min(1.0, current_volume + value * 0.01))
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Volume set to: {new_volume * 100:.2f}%)")
            
    if event == DialEventType.PUSH:
        global is_muted
        # Initialize COM library
        CoInitialize()
         # Adjust system volume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        is_muted = not is_muted
        volume.SetMute(is_muted, None)
        print(f"Muted: {is_muted}")
        update_key_image(deck, 1, True)
        update_touchscreen_image(deck)

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):

        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()))

        """touch = os.path.join(ASSETS_PATH, "long.png")"""
        
        # Set initial screen brightness to 30%.
        deck.set_brightness(60)

        # Set initial key images.
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)
        deck.set_dial_callback(dial_change_callback)
        deck.set_touchscreen_callback(touchscreen_event_callback)
        update_touchscreen_image(deck)
        
        """set_touchscreen_image(deck, touch)"""

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass