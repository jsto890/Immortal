const dgram = require('dgram');
const msgpack = require('msgpack-lite');

// Create a UDP socket (server)
const server = dgram.createSocket('udp4');

// Event listener for receiving messages
server.on('message', (msg, rinfo) => {
    try {
        const decodedMessage = msgpack.decode(msg); // Decode the msgpack message
        console.log(`Received data from ${rinfo.address}:${rinfo.port}:`, decodedMessage);

        if (decodedMessage.type === "key_event") {
            console.log(
                `Key Event: Key ${decodedMessage.key} ${decodedMessage.event}, Label: "${decodedMessage.value}"`
            );
        } else if (decodedMessage.type === "dial_event") {
            console.log(
                `Dial Event: Dial ${decodedMessage.dial} ${decodedMessage.event}, Label: ${decodedMessage.label}, Value: ${decodedMessage.value}`
            );
        } else if (decodedMessage.type === "touchscreen_event") {
            console.log(
                `Touchscreen Event: ${decodedMessage.event}, Label: ${decodedMessage.label}`
            );
        } else {
            console.error("Unknown event type:", decodedMessage.type);
        }
    } catch (err) {
        console.error("Error decoding message:", err);
    }
});

// Event listener for when the server starts listening
server.on('listening', () => {
    const address = server.address();
    console.log(`Server listening on ${address.address}:${address.port}`);
});

// Event listener for handling errors
server.on('error', (err) => {
    console.error(`Server error: ${err.stack}`);
    server.close();
});

// Bind the server to a specific port
const PORT = 41234; // This must match the client port
server.bind(PORT, '0.0.0.0');
