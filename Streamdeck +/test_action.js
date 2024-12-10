const usb = require('usb');

// Stream Deck USB Vendor and Product IDs
const VENDOR_ID = 0x0fd9; // Update this if needed
const PRODUCT_ID = 0x0084; // Update this if needed

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

// Find the input endpoint
const endpoint = iface.endpoints.find((ep) => ep.direction === 'in');
if (!endpoint) {
    console.error('No input endpoint found on the device');
    process.exit(1);
}
console.log('Input endpoint found:', endpoint.descriptor);

// Start listening for data
const maxPacketSize = endpoint.descriptor.wMaxPacketSize || 512;

endpoint.on('data', (data) => {
    try {
        // Extract the first 24 bytes for analysis
        const raw = data.slice(0, 12); // Adjusted to match the length of your example data

        // Convert raw data to a string for pattern matching
        const rawString = raw.toString('hex');

        // Categorize actions based on raw data patterns
        if (rawString.startsWith('01000800')) {
            // Button presses (Byte 4 to 11)
            for (let i = 4; i < 12; i++) {
                if (raw[i] === 1) {
                    console.log(`Button ${i - 4 + 1} pressed`);
                }
            }
        } else if (rawString.startsWith('01030500')) {
            // Dial actions (turns or presses)
            if (raw[4] === 0) {
                // Dial press (Byte 5 to 8)
                for (let i = 5; i < 9; i++) {
                    if (raw[i] === 1) {
                        console.log(`Dial ${i - 5 + 1} pressed`);
                    }
                }
            } else {
                // Dial turns (Byte 5 to 8 indicates deltas)
                for (let i = 5; i < 9; i++) {
                    const delta = raw.readInt8(i);
                    if (delta !== 0) {
                        const direction = delta > 0 ? 'R' : 'L';
                        console.log(`Dial ${i - 5 + 1} turned ${direction}`);
                    }
                }
            }
        } else {
            console.log('Unknown event type');
        }
    } catch (error) {
        console.error('Error processing data:', error.message);
    }
});

endpoint.on('error', (err) => {
    console.error('Endpoint error:', err);
});

endpoint.startPoll(1, maxPacketSize);

// Release resources on exit
process.on('exit', () => {
    console.log('Cleaning up before exit...');
    try {
        endpoint.stopPoll(() => {
            console.log('Polling stopped');
        });
    } catch (err) {
        console.error('Error stopping polling:', err);
    }

    try {
        iface.release(true, (err) => {
            if (err) console.error('Error releasing interface:', err);
            console.log('Device interface released');
        });
    } catch (err) {
        console.error('Error releasing interface:', err);
    }

    try {
        device.close();
        console.log('Device closed');
    } catch (err) {
        console.error('Error closing device:', err);
    }
});

// Handle uncaught exceptions to release resources
process.on('uncaughtException', (err) => {
    console.error('Uncaught exception:', err);
    process.exit(1);
});
