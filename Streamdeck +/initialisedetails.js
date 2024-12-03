const HID = require('node-hid');

function printDeckInfo(index, deck) {
    const keyImageFormat = deck.keyImageFormat();
    const touchscreenImageFormat = deck.touchscreenImageFormat();

    const flipDescription = {
        'false,false': "Not mirrored",
        'true,false': "Mirrored horizontally",
        'false,true': "Mirrored vertically",
        'true,true': "Mirrored horizontally and vertically"
    };

    console.log(`Deck ${index} - ${deck.deckType()}.`);
    console.log(`\t - ID: ${deck.id()}`);
    console.log(`\t - Serial: '${deck.getSerialNumber()}'`);
    console.log(`\t - Firmware version: '${deck.getFirmwareVersion()}'`);
    console.log(`\t - Key Count: ${deck.keyCount()} (in a ${deck.keyLayout()[0]} x ${deck.keyLayout()[1]} grid)`);

    if (deck.isVisual()) {
        console.log(`\t - Key Images: ${keyImageFormat.width} x ${keyImageFormat.height} pixels, ${keyImageFormat.format} format, rotated ${keyImageFormat.rotation} degrees, ${flipDescription[`${keyImageFormat.flipX},${keyImageFormat.flipY}`]}`);
        console.log(`\t - Touchscreen Images: ${touchscreenImageFormat.width} x ${touchscreenImageFormat.height} pixels, ${touchscreenImageFormat.format} format`);
    }
}

function main() {
    const devices = HID.devices();
    const streamDecks = devices.filter(device => device.vendorId === 0x0fd9 && device.productId === 0x0084); // Replace with actual vendorId and productId

    streamDecks.forEach((device, index) => {
        const deck = new HID.HID(device.path);
        printDeckInfo(index, deck);
        deck.close();
    });
}

main();