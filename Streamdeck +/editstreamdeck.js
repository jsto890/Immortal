const HID = require('node-hid');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

// Folder location of image assets used by this example.
const ASSETS_PATH = path.join(__dirname, 'Assets');

async function setKeyImage(deck, key, imagePath, text = null) {
    try {
        // Open the image file
        let icon = sharp(imagePath);

        // Convert the image to RGB mode if it's not already
        const metadata = await icon.metadata();
        if (metadata.channels !== 3) {
            icon = icon.toColourspace('rgb');
        }

        // Resize the image to fit the Stream Deck key
        const resizedImage = await icon.resize(deck.keyImageFormat().width, deck.keyImageFormat().height).toBuffer();

        // Draw text on the image if provided
        if (text) {
            const fontPath = path.join(ASSETS_PATH, 'AovelSansRounded-rdDL.ttf');  // Ensure you have a font file in the Assets folder
            const svgText = `
                <svg width="${deck.keyImageFormat().width}" height="${deck.keyImageFormat().height}">
                    <text x="50%" y="90%" font-family="${fontPath}" font-size="14" fill="white" text-anchor="middle">${text}</text>
                </svg>
            `;
            const textImage = await sharp(Buffer.from(svgText)).toBuffer();
            const combinedImage = await sharp(resizedImage).composite([{ input: textImage, gravity: 'south' }]).toBuffer();
            deck.setKeyImage(key, combinedImage);
        } else {
            deck.setKeyImage(key, resizedImage);
        }
    } catch (error) {
        console.error(`Error setting key image: ${error}`);
    }
}

// Example usage
async function main() {
    const devices = HID.devices();
    const streamDecks = devices.filter(device => device.vendorId === 4057 && device.productId === 132); // Replace with actual vendorId and productId

    if (streamDecks.length === 0) {
        console.log('No Stream Deck devices found.');
        return;
    }

    const deck = new HID.HID(streamDecks[0].path);
    await setKeyImage(deck, 0, path.join(ASSETS_PATH, 'example.png'), 'Hello World');
    deck.close();
}

main();