const dgram = require('dgram');
const msgpack = require('msgpack-lite');

// Configuration - these can be overridden with environment variables
const PORT = parseInt(process.env.UDP_PORT || '41234'); // This must match the client port

// Configuration note for users
const CONFIG_NOTE = `
IMPORTANT: This project was developed during a summer internship. 
Some configurations may be specific to the development environment.

Current configuration:
- UDP Port: ${PORT}

To customize, set environment variables:
- UDP_PORT=41234
`;

console.log(CONFIG_NOTE);

// Create a UDP socket (server)
const server = dgram.createSocket('udp4');

// Function to get the real-time clock in HH:MM:SS:MMM format
function getRealTimeClockWithMilliseconds() {
    const now = new Date();

    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    const milliseconds = now.getMilliseconds().toString().padStart(3, '0');

    return `${hours}:${minutes}:${seconds}:${milliseconds}`;
}

// Function to convert frames to milliseconds and get the timecode in HH:MM:SS:MMM
function convertFramesToMillisecondsAndFormat(timecode) {
    const match = timecode.match(/(\d{2}):(\d{2}):(\d{2}):(\d{2}) @ (\d+)/);
    if (!match) {
        console.error('Invalid timecode format');
        return null;
    }

    const [, hh, mm, ss, ff, fps] = match.map(Number);

    // Convert frames to milliseconds
    const frameMilliseconds = (ff / fps) * 1000;

    // Format the timecode with milliseconds
    const formattedTimecode = `${hh.toString().padStart(2, '0')}:${mm
        .toString()
        .padStart(2, '0')}:${ss.toString().padStart(2, '0')}:${Math.round(
        frameMilliseconds
    )
        .toString()
        .padStart(3, '0')}`;

    return formattedTimecode;
}

// Function to calculate time difference in HH:MM:SS:MMM format
function calculateTimeDifference(start, end) {
    const startParts = start.split(':').map(Number);
    const endParts = end.split(':').map(Number);

    // Convert both to total milliseconds
    const startMilliseconds =
        startParts[0] * 3600000 + // Hours to milliseconds
        startParts[1] * 60000 + // Minutes to milliseconds
        startParts[2] * 1000 + // Seconds to milliseconds
        startParts[3]; // Milliseconds

    const endMilliseconds =
        endParts[0] * 3600000 +
        endParts[1] * 60000 +
        endParts[2] * 1000 +
        endParts[3];

    // Calculate the difference in milliseconds
    let differenceMilliseconds = endMilliseconds - startMilliseconds;

    // Handle negative differences by adding 24 hours in milliseconds
    if (differenceMilliseconds < 0) {
        differenceMilliseconds += 24 * 3600000;
    }

    // Convert back to HH:MM:SS:MMM format
    const hours = Math.floor(differenceMilliseconds / 3600000);
    differenceMilliseconds %= 3600000;
    const minutes = Math.floor(differenceMilliseconds / 60000);
    differenceMilliseconds %= 60000;
    const seconds = Math.floor(differenceMilliseconds / 1000);
    const milliseconds = differenceMilliseconds % 1000;

    return `${hours.toString().padStart(2, '0')}:${minutes
        .toString()
        .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}:${milliseconds
        .toString()
        .padStart(3, '0')}`;
}

// Function to compare two clock formats
function compareClocks(receivedTime, realTime) {
    console.log(`Received Timecode Clock: ${receivedTime}`);
    console.log(`Real-Time Clock: ${realTime}`);

    const difference = calculateTimeDifference(receivedTime, realTime);
    console.log(`Difference in time: ${difference}`);
}

// Event listener for receiving messages
server.on('message', (msg, rinfo) => {
    try {
        const decodedMessage = msgpack.decode(msg); // Decode the msgpack message
        console.log(`Received data:`, decodedMessage);

        if (decodedMessage.type === "timecode") {
            const timecode = decodedMessage.timecode;
            console.log(`Received Timecode: "${timecode}" from ${rinfo.address}:${rinfo.port}`);

            // Convert the received timecode
            const receivedTimeWithMilliseconds = convertFramesToMillisecondsAndFormat(timecode);
            if (!receivedTimeWithMilliseconds) return;

            // Get real-time clock
            const realTimeClock = getRealTimeClockWithMilliseconds();

            // Compare the two clocks
            compareClocks(receivedTimeWithMilliseconds, realTimeClock);
        } else {
            console.error("Invalid message type");
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
server.bind(PORT, '0.0.0.0');
