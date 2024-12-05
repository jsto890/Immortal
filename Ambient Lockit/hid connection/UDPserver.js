const dgram = require('dgram');

// Create a UDP socket (server)
const server = dgram.createSocket('udp4');

// Event listener for receiving messages
server.on('message', (msg, rinfo) => {
    console.log(`Received message: "${msg}" from ${rinfo.address}:${rinfo.port}`);
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