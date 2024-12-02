const HID = require('node-hid'); // import hid

try {
    // Replace with your device's vendorId and productId
    const vendorId = 0x10E6;
    const productId = 0x108C;

    // Open the device
    const device = new HID.HID(vendorId, productId);
    console.log('Device opened');

    // Example of handling an error during device interaction
    device.on('error', (error) => {
        console.log(`Error: ${error}`);
        device.close();
        console.log("Device closed");
    });

    // Your code to interact with the device goes here

} catch (error) {
    console.log(`Error: ${error}`);
    if (device) {
        device.close();
        console.log('Device closed');
    }
}
