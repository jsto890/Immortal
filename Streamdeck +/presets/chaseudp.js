const dgram = require('dgram');
const readline = require('readline');
const msgpack = require('msgpack-lite');

// Create a UDP socket (server)
const server = dgram.createSocket('udp4');

// Create an interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

// Configuration - these can be overridden with environment variables
const PYTHON_UDP_IP = process.env.UDP_IP || "127.0.0.1"; // Replace with Python script's IP
const PYTHON_UDP_PORT = parseInt(process.env.RECEIVE_PORT || "41235"); // Port for receiving messages in Python

// Configuration note for users
const CONFIG_NOTE = `
IMPORTANT: This project was developed during a summer internship. 
Some configurations may be specific to the development environment.

Current configuration:
- Python UDP IP: ${PYTHON_UDP_IP}
- Python UDP Port: ${PYTHON_UDP_PORT}

To customize, set environment variables:
- UDP_IP=192.168.1.100
- RECEIVE_PORT=41235
`;

console.log(CONFIG_NOTE);

// Event listener for receiving messages
server.on('message', (msg, rinfo) => {
    try {
        const decodedMessage = msgpack.decode(msg);
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
        } else if (decodedMessage.type === "label_update") {
            // Handle label updates from Python
            console.log(`Label Update for Layer: ${decodedMessage.layer}, Target: ${decodedMessage.target}, Index: ${decodedMessage.index}, Label: ${decodedMessage.label}, Image: ${decodedMessage.image}`);
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

// Function to send messages to the Python script
function sendToPython(data) {
    const udpSocket = dgram.createSocket('udp4');
    const message = msgpack.encode(data);
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
        "Do you want to change a 'key', 'dial', or 'touchscreen'? ",
        (target) => {
            if (target === "key" || target === "dial" || target === "touchscreen") {
                rl.question(
                    "Which layer do you want to update? (1-3) ",
                    (layerInput) => {
                        const layer = parseInt(layerInput);
                        if (![1,2,3].includes(layer)) {
                            console.log("Invalid layer. Please enter 1, 2, or 3.");
                            return promptUser();
                        }

                        // If target is touchscreen, index might not be relevant.
                        // Assume index is needed for key/dial but not for touchscreen.
                        if (target === "touchscreen") {
                            // Touchscreen update might just have lines or other data
                            // For simplicity, let's just update the 'lines' here.
                            rl.question("Enter new lines (comma separated): ", (lineInput) => {
                                const lines = lineInput.split(",").map(line => line.trim());
                                const data = {
                                    type: "update_label",
                                    layer: layer,
                                    target: target,
                                    // Instead of index, we pass touchscreen_data:
                                    touchscreen_data: { lines: lines }
                                };
                                sendToPython(data);
                                promptUser();
                            });
                        } else {
                            rl.question(
                                `What ${target} index do you want to change? (key:0-7, dial:0-3) `,
                                (number) => {
                                    const index = parseInt(number);
                                    // Validate index
                                    if (target === "key" && (index < 0 || index > 7)) {
                                        console.log("Invalid key index. Must be between 0 and 7.");
                                        return promptUser();
                                    }
                                    if (target === "dial" && (index < 0 || index > 3)) {
                                        console.log("Invalid dial index. Must be between 0 and 3.");
                                        return promptUser();
                                    }

                                    rl.question("Enter the new label: ", (newLabel) => {
                                        rl.question("Enter the new image filename (or leave blank for none): ", (newImage) => {
                                            const data = {
                                                type: "update_label",
                                                layer: layer,
                                                target: target,
                                                index: index,
                                                label: newLabel
                                            };
                                            
                                            // Include image if provided
                                            if (newImage.trim() !== "") {
                                                data.image = newImage.trim();
                                            }

                                            sendToPython(data); 
                                            promptUser();
                                        });
                                    });
                                }
                            );
                        }
                    }
                );
            } else {
                console.log("Invalid input. Please enter 'key', 'dial', or 'touchscreen'.");
                promptUser(); // Restart prompt
            }
        }
    );
}

// Bind the server to a specific port
const PORT = parseInt(process.env.UDP_PORT || "41234"); // This must match the client port
server.bind(PORT, '0.0.0.0');
