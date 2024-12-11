const dgram = require('dgram');
const readline = require('readline');
const msgpack = require('msgpack-lite');
const fs = require('fs');

// Create a UDP socket (server)
const server = dgram.createSocket('udp4');

// Create an interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

// Python server details
const PYTHON_UDP_IP = "192.168.1.200"; // Replace with Python script's IP
const PYTHON_UDP_PORT = 41235; // Port for receiving messages in Python

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
    promptUser(); // Start user interaction
});

// Event listener for handling errors
server.on('error', (err) => {
    console.error(`Server error: ${err.stack}`);
    server.close();
});

function sendImage(label) {
    const imagePath = `/home/root/STREAMDECK/py_files/Assets/testphotos/${label}.png`;
    const udpSocket = dgram.createSocket('udp4');
    const imageBuffer = fs.readFileSync(imagePath);

    const CHUNK_SIZE = 64000;
    for (let i = 0; i < imageBuffer.length; i += CHUNK_SIZE) {
        const chunk = imageBuffer.slice(i, i + CHUNK_SIZE);
        udpSocket.send(chunk, 0, chunk.length, 41236, PYTHON_UDP_IP, (err) => {
            if (err) console.error("Error sending chunk:", err);
            else console.log(`Chunk sent: ${i / CHUNK_SIZE}`);
        });
    }

    udpSocket.send(Buffer.from("END"), 0, 3, 41236, PYTHON_UDP_IP, (err) => {
        if (err) console.error("Error sending end marker:", err);
        else console.log("End marker sent.");
        udpSocket.close();
    });

    console.log("Image sent.");
}

// Function to send messages to the Python script
function sendToPython(data) {
    const udpSocket = dgram.createSocket('udp4');
    const message = msgpack.encode(data); // Ensure proper msgpack format
    udpSocket.send(message, PYTHON_UDP_PORT, PYTHON_UDP_IP, (err) => {
        if (err) {
            console.error("Error sending message to Python:", err);
        } else {
            console.log("Message sent to Python:", data);
        }
        udpSocket.close();
    });
}

// Prompt the user for input
function promptUser() {
    rl.question(
        "Do you want to change a key or dial? (Enter 'key' or 'dial') ",
        (type) => {
            if (type === "key" || type === "dial") {
                rl.question(
                    `What number ${type} (0-${type === "key" ? 6 : 3})? `,
                    (number) => {
                        rl.question("What do you want to change it to? ", (newLabel) => {
                            const data = {
                                type: "update_label",
                                target: type,
                                index: parseInt(number),
                                label: newLabel,
                            };
                            sendToPython(data); // Send update to Python
                            sendImage(newLabel);
                            promptUser(); // Restart prompt
                        });
                    }
                );
            } else {
                console.log("Invalid input. Please enter 'key' or 'dial'.");
                promptUser(); // Restart prompt
            }
        }
    );
}

// Bind the server to a specific port
const PORT = 41234; // This must match the client port
server.bind(PORT, '0.0.0.0');
