from StreamDeck.DeviceManager import DeviceManager

def print_deck_info(index, deck):
    key_image_format = deck.key_image_format()
    touchscreen_image_format = deck.touchscreen_image_format()
    
    flip_description = {
        (False, False): "Not mirrored",
        (True, False): "Mirrored horizontally",
        (False, True): "Mirrored vertically",
        (True, True): "Mirrored horizontally and vertically"
    }
    
    print("Deck {} - {}.".format(index, deck.deck_type()))
    print("\t - ID: {}".format(deck.id()))
    print("\t - Serial: '{}'".format(deck.get_serial_number()))
    print("\t - Firmware version: '{}'".format(deck.get_firmware_version()))
    print("\t - Key Count: {} (in a {} x {} grid)".format(
        deck.key_count(), 
        deck.key_layout()[0], 
        deck.key_layout()[1]))
    
    if deck.is_visual():
        print("\t - Key Images: {} x {} pixels, {} format, rotated {} degrees, {}".format(
            key_image_format['size'][0], 
            key_image_format['size'][1], 
            key_image_format['format'], 
            key_image_format['format'], 
            key_image_format['rotation'], 
            flip_description[key_image_format['flip']]))
        
        if deck.is_touch():
            print("\t - Touchscreen: {} x {} pixels, {} format, rotated {} degrees, {}".format(
                touchscreen_image_format['size'][0], 
                touchscreen_image_format['size'][1], 
                touchscreen_image_format['format'], 
                touchscreen_image_format['rotation'], 
                flip_description[touchscreen_image_format['flip']]))
    else:
        print("\t - No images supported.")
        
if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()
    
    print("Found {} Stream Decks.\n".format(len(streamdecks)))
    
    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()
        
        print_deck_info(index, deck)
        
        deck.close()
        
