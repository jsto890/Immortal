const dgram = require('dgram');
const readline = require('readline');
const msgpack = require('msgpack-lite');

const PYTHON_UDP_IP = "192.168.1.200"; // Replace with Python script's IP
const PYTHON_UDP_PORT = 41235; // Port for receiving messages in Python

// Create a UDP socket (server)
const server = dgram.createSocket('udp4');

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

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

function askQuestion(query) {
    return new Promise((resolve) => {
        rl.question(query, (answer) => {
            resolve(answer.trim());
        });
    });
}

function sendToPython(data) {
    return new Promise((resolve, reject) => {
        const udpSocket = dgram.createSocket('udp4');
        const message = msgpack.encode(data);
        udpSocket.send(message, 0, message.length, PYTHON_UDP_PORT, PYTHON_UDP_IP, (err) => {
            if (err) {
                console.error("Error sending message to Python:", err);
                udpSocket.close();
                reject(err);
            } else {
                console.log("Message sent to Python:", data);
                udpSocket.close();
                resolve();
            }
        });
    });
}

// Define a preset example
// This can be adjusted to any combination of "update_image_link" and "update_label" messages.
const PRESET_MESSAGES = [
    {
        // Upload image for layer 1 key 7
        type: "update_image_link",
        //image_url: ,
        filename: "power_on.png"
    },
    {
        // Upload image for layer 2 key 3
        type: "update_image_link",
        //image_url: ,
        filename: "mode.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 0,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 1,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 2,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 3,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 4,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 5,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 7 in layer 1 to use power_on.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 6,
        label: "",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 1,
        target: "key",
        index: 7,
        label: "Power",
        image: "power_on.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 2,
        target: "key",
        index: 0,
        label: "Breadcrumbs on/off",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 2,
        target: "key",
        index: 1,
        label: "Speedometer on/off",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 2,
        target: "key",
        index: 2,
        label: "POI on/off",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 2,
        target: "key",
        index: 4,
        label: "Map on/off",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 2,
        target: "key",
        index: 5,
        label: "Ticker on/off",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 2,
        target: "key",
        index: 6,
        label: "Street on/off",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 3,
        target: "key",
        index: 0,
        label: "Breadcrumbs Replay",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 3,
        target: "key",
        index: 1,
        label: "Map Size",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 3,
        target: "key",
        index: 2,
        label: "Map Position",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 3,
        target: "key",
        index: 4,
        label: "Brightness",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 3,
        target: "key",
        index: 5,
        label: "Ticker Speed",
        image: "image_1.png"
    },
    {
        // Set key 3 in layer 2 to mode.png
        type: "update_label",
        layer: 3,
        target: "key",
        index: 6,
        label: "Volume",
        image: "image_1.png"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 2,
        target: "dial",
        index: 0,
        label: "Breadcrumbs"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 2,
        target: "dial",
        index: 1,
        label: "POI"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 2,
        target: "dial",
        index: 2,
        label: "Speedometer"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 2,
        target: "dial",
        index: 3,
        label: "Map"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 3,
        target: "dial",
        index: 0,
        label: "Ticker"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 3,
        target: "dial",
        index: 1,
        label: "Street"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 3,
        target: "dial",
        index: 2,
        label: "Brightness"
    },
    {
        // Example dial label in layer 2
        type: "update_label",
        layer: 3,
        target: "dial",
        index: 3,
        label: "Exit"
    },
    {
        // Example touchscreen lines in layer 2
        type: "update_label",
        layer: 2,
        target: "touchscreen",
        touchscreen_data: {
            lines: ["Preset Ticker", "Layer 2 Screen"]
        }
    },
    {
        // Example touchscreen lines in layer 2
        type: "update_label",
        layer: 3,
        target: "touchscreen",
        touchscreen_data: {
            lines: ["Preset Ticker", "Layer 3 Screen"]
        }
    }
];

async function applyPreset() {
    console.log("Applying Stream Deck preset...");
    // Send each message in PRESET_MESSAGES
    for (const msg of PRESET_MESSAGES) {
        await sendToPython(msg);
    }
    console.log("Preset applied successfully!");
}

async function promptUser() {
    try {
        const target = await askQuestion("Do you want to change a 'key', 'dial', 'touchscreen', or 'preset'? ");

        if (target === "key" || target === "touchscreen" || target === "dial") {
            const layerInput = await askQuestion("Which layer do you want to update? (1-3) ");
            const layer = parseInt(layerInput);
            if (![1,2,3].includes(layer)) {
                console.log("Invalid layer. Please enter 1, 2, or 3.");
                return promptUser(); // Go back to start
            }

            let index;
            if (target === "key") {
                index = parseInt(await askQuestion("What key index do you want to change? (0-7) "));
                if (index < 0 || index > 7) {
                    console.log("Invalid key index. Must be between 0 and 7.");
                    return promptUser(); // Go back to start
                }

                // Step 1: Ask user for image URL and filename
                const image_url = await askQuestion("Enter the image URL: ");
                const filename = await askQuestion("Enter the filename to save as (e.g., my_image.png): ");

                // Step 2: Send update_image_link message to Python to download the image
                await sendToPython({
                    type: "update_image_link",
                    image_url: image_url,
                    filename: filename
                });

                console.log("Image upload request sent. The image should now be available in the Assets folder on the Python side.");

                // For key: ask label and image
                const newLabel = await askQuestion("Enter the new label: ");
                const newImage = await askQuestion(`Enter the image filename to use (e.g., ${filename}): `);

                const data = {
                    type: "update_label",
                    layer: layer,
                    target: target,
                    index: index,
                    label: newLabel
                };
                if (newImage.trim() !== "") {
                    data.image = newImage.trim();
                }

                await sendToPython(data);
                console.log("Key updated successfully.");
                return promptUser(); // Ask again

            } else if (target === "touchscreen") {
                // Touchscreen: No lines needed, only optional image
                const useImage = await askQuestion(`Do you want to set an image for the touchscreen? (yes/no) `);
                let tsData = {};

                if (useImage.toLowerCase() === "yes") {
                    // Step 1: Ask user for image URL and filename
                    const image_url = await askQuestion("Enter the image URL: ");
                    const filename = await askQuestion("Enter the filename to save as (e.g., my_image.png): ");

                    // Step 2: Send update_image_link message to Python to download the image
                    await sendToPython({
                        type: "update_image_link",
                        image_url: image_url,
                        filename: filename
                    });

                    console.log("Image upload request sent. The image should now be available in the Assets folder on the Python side.");

                    const tsImage = await askQuestion(`Enter the image filename to use (e.g., ${filename}): `);
                    if (tsImage.trim() !== "") {
                        tsData.image = tsImage.trim();
                    }
                }

                const data = {
                    type: "update_label",
                    layer: layer,
                    target: target,
                    touchscreen_data: tsData
                };

                await sendToPython(data);
                console.log("Touchscreen updated successfully.");
                return promptUser(); // Ask again

            } else if (target === "dial") {
                // Dials have no images, just label
                index = parseInt(await askQuestion("What dial index do you want to change? (0-3) "));
                if (index < 0 || index > 3) {
                    console.log("Invalid dial index. Must be between 0 and 3.");
                    return promptUser(); // Go back to start
                }
                const newLabel = await askQuestion("Enter the new label: ");
                const data = {
                    type: "update_label",
                    layer: layer,
                    target: target,
                    index: index,
                    label: newLabel
                };
                await sendToPython(data);
                console.log("Dial updated successfully.");
                return promptUser(); // Ask again
            }

        } else if (target.toLowerCase() === "preset") {
            // If user chooses "preset"
            await applyPreset();
            return promptUser();

        } else {
            console.log("Invalid input. Please enter 'key', 'dial', 'touchscreen', or 'preset'.");
            return promptUser(); // Restart prompt
        }

    } catch (error) {
        console.error("Error:", error);
        return promptUser(); // Try asking again on error
    }
}

promptUser(); // Start the loop

// Bind the server to a specific port
const PORT = 41234; // Must match the client port (Python script's send_udp_message destination)
server.bind(PORT, '0.0.0.0');
