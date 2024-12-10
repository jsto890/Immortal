const usb = require('usb');
const sharp = require('sharp');

const VENDOR_ID = 0x0fd9; // Elgato's Vendor ID
const PRODUCT_ID = 0x0084; // Stream Deck Plus Product ID

// Find the Stream Deck device
const device = usb.findByIds(VENDOR_ID, PRODUCT_ID);

if (!device) {
    console.error('Stream Deck device not found. Ensure the device is connected and IDs are correct.');
    process.exit(1);
}

console.log('Stream Deck device found:', {
    busNumber: device.busNumber,
    deviceAddress: device.deviceAddress,
    deviceDescriptor: device.deviceDescriptor,
});

// Open the device
device.open();

// Claim the interface
const iface = device.interfaces[0];
if (iface.isKernelDriverActive()) {
    console.log('Detaching kernel driver...');
    iface.detachKernelDriver();
}
iface.claim();
console.log('Device interface claimed');

// Find the output endpoint
const outEndpoint = iface.endpoints.find((ep) => ep.direction === 'out');
if (!outEndpoint) {
    console.error('No output endpoint found on the device');
    process.exit(1);
}
console.log('Output endpoint found:', outEndpoint.descriptor);

// Function to prepare an image for a button
async function prepareImage(filePath, width = 288, height = 288) {
    console.log(`Preparing image from: ${filePath}`);
    return sharp(filePath)
        .resize(width, height)
        .raw() // Get raw RGB data
        .toBuffer()
        .then(buffer => {
            console.log(`Image prepared successfully. Buffer length: ${buffer.length}`);
            return buffer;
        })
        .catch(err => {
            console.error('Error:', err);
            throw err;
        });
}

// Function to send the image to a button
async function setButtonImage(buttonIndex, filePath) {
    try {
        console.log(`Starting to set button image for button ${buttonIndex}`);
        const imageBuffer = await prepareImage(filePath);

        console.log(`Image buffer prepared for button ${buttonIndex}`);

        // Construct the command to send the image
        const header = Buffer.alloc(32);
        header.writeUInt8(0x02, 0); // Command for setting an image
        header.writeUInt8(buttonIndex, 1); // Button index

        console.log(`Header constructed: ${header.toString('hex')}`);

        // Combine header and image data
        const command = Buffer.concat([header, imageBuffer]);

        console.log(`Command constructed. Total length: ${command.length}`);

        // Send the command
        console.log(`Sending image to button ${buttonIndex}...`);
        outEndpoint.transfer(command, (err) => {
            if (err) {
                console.error('Error sending image to button:', err);
            } else {
                console.log(`Image sent to button ${buttonIndex}`);
            }
        });
        console.log(`Transfer initiated for button ${buttonIndex}`);
    } catch (err) {
        console.error('Error in setButtonImage:', err);
    }
}

// Example: Set an image on button 1
setButtonImage(0, '/home/root/STREAMDECK/js_files/ASSETS/immortal.jpg');


// Clean up on exit
process.on('exit', () => {
    iface.release(true, () => {
        device.close();
    });
});