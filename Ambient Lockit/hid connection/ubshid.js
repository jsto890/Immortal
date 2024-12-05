const HID = require('node-hid');

// Set driver type to "libusb" for Linux
HID.setDriverType("libusb");

// Specify vendor and product IDs
const targetVendorID = 0x10e6; // Lockit vendor ID
const targetProductID = 0x108c; // Lockit product ID

// Find the target device
const devices = HID.devices().filter(device =>
    device.vendorId === targetVendorID && device.productId === targetProductID
);

// Log found devices and initialize if available
if (devices.length > 0) {
    console.log('Found matching device:', device);
    const device = new HID.HID(targetVendorID, targetProductID);

    // Function to send a command and wait for a response
    const sendCommand = (command, tag) => {
        return new Promise((resolve, reject) => {
            const paddedCommand = Buffer.alloc(64, 0); // 64-byte packet
            paddedCommand.write(command, 0, 'ascii'); // Write the command into the buffer
            device.write([0, ...paddedCommand]); // Endpoint 0 for HID
            
            device.read((err, data) => {
                if (err) return reject(err);
                const response = data.toString('ascii').replace(/\0/g, ''); // Clean null bytes
                if (response.startsWith(tag)) {
                    resolve(response);
                } else {
                    reject(new Error('Unexpected response: ' + response));
                }
            });
        });
    };

    // Example: Set Frame Format
    const setFrameFormat = async (newFrameFormat) => {
        const frameIndex = {
            0: "23.976",
            1: "24",
            2: "25",
            3: "29.97",
            4: "30",
            5: "29.97 drop",
            6: "30 drop",
            7: "47.96",
            8: "48",
            9: "50",
            10: "59.94",
            11: "60"
        };
        const command = `*A86*I0:${newFrameFormat}*Z`;
        const tag = "*A86*Z";

        try {
            const response = await sendCommand(command, tag);
            console.log(`Frame format set to: ${frameIndex[newFrameFormat]}`);
        } catch (error) {
            console.error('Error setting frame format:', error.message);
        }
    };

    // Example: Set ACN Channel
    const setACNChannel = async (channel) => {
        if (channel < 11 || channel > 26) {
            console.error('Invalid ACN channel. Must be between 11 and 26.');
            return;
        }
        const command = `*A9*I0:${channel}*Z`;
        const tag = "*A9*Z";

        try {
            const response = await sendCommand(command, tag);
            console.log(`ACN channel set to: ${channel}`);
        } catch (error) {
            console.error('Error setting ACN channel:', error.message);
        }
    };

    // Example: Enable LTC Callback
    const enableLTCCallback = async (enable) => {
        const command = `*A6*I0:${enable ? 1 : 0}*Z`;
        const tag = "*A6*Z";

        try {
            const response = await sendCommand(command, tag);
            console.log(`LTC callback ${enable ? 'enabled' : 'disabled'}`);
        } catch (error) {
            console.error('Error toggling LTC callback:', error.message);
        }
    };

    // Example usage
    (async () => {
        await setFrameFormat(4); // Set to 30 fps
        await setACNChannel(12); // Set ACN channel to 12
        await enableLTCCallback(true); // Enable LTC callback
    })();

} else {
    console.error('No matching device found with Vendor ID:', targetVendorID, 'and Product ID:', targetProductID);
}
