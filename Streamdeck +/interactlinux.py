import os
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

# Generates a custom tile with an image via the PIL module.
def render_key_image(deck, icon_filename, label_text=""):
    # Load the image asset for the button.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_key_image(deck, icon)

    # Optionally overlay text on the image.
    if label_text:
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(os.path.join(ASSETS_PATH, "AovelSansRounded-rdDL.ttf"), 14)
        draw.text((image.width / 2, image.height - 20), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_key_format(deck, image)

# Updates the key image on the Stream Deck.
def update_key_image(deck, key, image_path):
    # Generate the image for the key.
    image = render_key_image(deck, image_path)

    # Set the image on the specified key.
    with deck:
        deck.set_key_image(key, image)

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()))

        # Set initial brightness.
        deck.set_brightness(50)

        # Set images for each button.
        for key in range(deck.key_count()):
            # Use different images for each button. Adjust paths as needed.
            image_path = os.path.join(ASSETS_PATH, f"image_{key + 1}.png")
            if os.path.exists(image_path):
                update_key_image(deck, key, image_path)
            else:
                print(f"Image not found for key {key}: {image_path}")

        # Wait until all application threads have terminated (e.g., when the user closes the
        input("Press Enter to exit...")

        # Reset the Stream Deck before exiting.
        deck.reset()
        deck.close()

