import os
import io
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

def set_key_image(deck, key, image_path, text=None):
    # Open the image file
    icon = Image.open(image_path)

    # Convert the image to RGB mode if it's not already
    if icon.mode != 'RGB':
        icon = icon.convert('RGB')

    # Resize the image to fit the Stream Deck key
    image = PILHelper.create_scaled_key_image(deck, icon)
    
        # Draw text on the image if provided
    if text:
        draw = ImageDraw.Draw(image)
        font_path = os.path.join(ASSETS_PATH, "AovelSansRounded-rdDL.ttf")  # Ensure you have a font file in the Assets folder
        font = ImageFont.truetype(font_path, 14)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
        draw.text(text_position, text, font=font, fill="white")

    # Convert the image to the native format of the Stream Deck
    native_image = PILHelper.to_native_key_format(deck, image)

    # Set the image on the specified key
    deck.set_key_image(key, native_image)

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

if __name__ == "__main__":
    # Enumerate all connected Stream Deck devices
    streamdecks = DeviceManager().enumerate()

    if len(streamdecks) == 0:
        print("No Stream Deck devices found.")
        exit()

    # Use the first Stream Deck device
    deck = streamdecks[0]

    # Open the Stream Deck device
    deck.open()

    # Reset the Stream Deck device
    deck.reset()

    # Set the brightness of the Stream Deck
    deck.set_brightness(60)

    # Path to the image files
    IMMORTAL = os.path.join(ASSETS_PATH, "immortal.png")
    touch = os.path.join(ASSETS_PATH, "long.png")
    whitesquare = os.path.join(ASSETS_PATH, "whitesquare.jpg")

    # Set the image on the specified key
    set_key_image(deck, 0, IMMORTAL)
    set_key_image(deck, 1, whitesquare, text="Speed Camera")

    # Set the image on the touchscreen
    set_touchscreen_image(deck, touch)

    # Keep the script running to maintain the image on the key
    input("Press Enter to exit...")

    # Close the Stream Deck device
    deck.close()