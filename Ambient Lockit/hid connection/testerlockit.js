const HID = require('node-hid');
const { TextEncoder, TextDecoder } = require('util');

// Set driver type to "libusb" for Linux
HID.setDriverType("libusb");

// Specify vendor and product IDs
const targetVendorID = 0x10e6; // Lockit vendor ID
const targetProductID = 0x108c; // Lockit product ID

module.exports = class ACNLockit {
    constructor() {
        const devices = HID.devices().filter(device =>
            device.vendorId === targetVendorID && device.productId === targetProductID
        );

        this.errorCode = {
            "400": "Generic Error",
            "402": "Argument Missing",
            "601": "Argument Invalid"
        };

        if (devices.length > 0) {
            console.log('Found matching device:', devices[0]);
            this.unit = new HID.HID(targetVendorID, targetProductID);

            // Add listener for notifications
            this.unit.on("data", (data) => {
                const response = new TextDecoder().decode(data).replace(/\0/g, "");
                if (response.startsWith("*C0")) {
                    console.log("Notification received:", response);
                    const parsedTimecode = this.parseLTCResponse(response);
                    console.log("Parsed Timecode:", parsedTimecode);
                }
            });

            this.unit.on("error", (err) => {
                console.error("Device error:", err);
            });
        } else {
            console.error("No matching device found.");
            this.unit = null;
        }
    }

    // Helper function for encoding and writing
    sendCommand(command, expectedTag, callback) {
        if (!this.unit) {
            console.error('Error: Device not initialized.');
            return;
        }

        try {
            const utfEncoder = new TextEncoder();
            const encodedCommand = utfEncoder.encode(command);
            this.unit.write(encodedCommand);

            const readResponse = () => {
                this.unit.read((err, data) => {
                    if (err) {
                        console.error("Error reading response:", err);
                    } else {
                        const response = new TextDecoder().decode(data).replace(/\0/g, ""); // Remove null bytes
                        if (response.startsWith("*C0")) {
                            console.log("Notification received:", response);
                            readResponse(); // Read the next response
                        } else if (expectedTag && !response.startsWith(expectedTag)) {
                            console.error("Unexpected response:", response);
                        } else {
                            callback(response);
                        }
                    }
                });
            };

            readResponse(); // Start reading the response
        } catch (e) {
            console.error("Error writing command:", e);
        }
    }

    parseLTCResponse(msg) {
        const rawLTC = msg.split("*I0:")[1].split("*")[0];
        const fps = parseInt(msg.split("*I1:")[1].split("*")[0], 10);
    
        // Convert raw LTC to a 64-bit binary string
        const rawrLTCBin = BigInt(`0x${rawLTC}`).toString(2).padStart(64, "0");
        const rawLTCBin = rawrLTCBin.split("").reverse().join("");
    
        // Extract timecode components
        const framesUnits = parseInt((rawLTCBin.slice(0, 4)).split("").reverse().join(""), 2);
        const framesTens = parseInt((rawLTCBin.slice(8, 10)).split("").reverse().join(""), 2);
        const frames = framesUnits + (framesTens * 10);
    
        const secondsUnits = parseInt((rawLTCBin.slice(16, 20)).split("").reverse().join(""), 2);
        const secondsTens = parseInt((rawLTCBin.slice(24, 27)).split("").reverse().join(""), 2);
        const seconds = secondsUnits + (secondsTens * 10);
    
        const minutesUnits = parseInt((rawLTCBin.slice(32, 36)).split("").reverse().join(""), 2);
        const minutesTens = parseInt((rawLTCBin.slice(40, 43)).split("").reverse().join(""), 2);
        const minutes = minutesUnits + (minutesTens * 10);
    
        const hoursUnits = parseInt((rawLTCBin.slice(48, 52)).split("").reverse().join(""), 2);
        const hoursTens = parseInt((rawLTCBin.slice(56, 58)).split("").reverse().join(""), 2);
        const hours = hoursUnits + (hoursTens * 10);
    
        // Format the timecode string
        const timecode = `${hours.toString().padStart(2, "0")}:${minutes
            .toString()
            .padStart(2, "0")}:${seconds
            .toString()
            .padStart(2, "0")}:${frames
            .toString()
            .padStart(2, "0")} @ ${fps} fps`;
    
        return timecode;
    }

    // Set Frame Format
    setFrameFormat(newFrameFormat) {
        const command = `*A86*I0:${newFrameFormat}*Z`;
        this.sendCommand(command, "*A86*Z", (response) => {
            console.log("Set Frame Format Response:", response);
        });
    }

    // Get Frame Format
    getFrameFormat() {
        const command = "*Q2*Z";
        this.sendCommand(command, "*Q2", (response) => {
            console.log("Get Frame Format Response:", response);
        });
    }

    // Get Sync
    getSync() {
        const command = "*A49*Z";
        this.sendCommand(command, "*A49", (response) => {
            console.log("Get Sync Response:", response);
        });
    }

    // Reset Timecode
    resetTime() {
        const command = "*A35*I0:00000000*Z";
        this.sendCommand(command, "*A35*Z", (response) => {
            console.log("Timecode Reset Response:", response);
        });
    }

    // Set Timecode
    setTimeCode(newTimeCode) {
        const command = `*A35*I0:${newTimeCode}*Z`;
        this.sendCommand(command, "*A35*Z", (response) => {
            console.log("Set Timecode Response:", response);
        });
    }

    // Set ACN Channel
    setACNChannel(newACNChannel) {
        if (newACNChannel < 11 || newACNChannel > 26) {
            console.error("Invalid ACN Channel: Must be between 11 and 26.");
            return;
        }
        const command = `*A9*I0:${newACNChannel}*Z`;
        this.sendCommand(command, "*A9*Z", (response) => {
            console.log("Set ACN Channel Response:", response);
        });
    }

    // Get ACN Channel
    getACNChannel() {
        const command = "*Q1*Z";
        this.sendCommand(command, "*Q1", (response) => {
            console.log("Get ACN Channel Response:", response);
        });
    }

    // Get Miscellaneous Information
    getMisc() {
        const command = "*Q35*Z";
        this.sendCommand(command, "*Q35", (response) => {
            console.log("Miscellaneous Information:", response);
        });
    }

    // Reset Device
    reset() {
        const command = "*A4*Z";
        this.sendCommand(command, "*A4*Z", (response) => {
            console.log("Device Reset Response:", response);
        });
    }

    // Set Sync Format
    setSyncFormat(newSyncMode, newSyncFormat, newSyncRate) {
        const command = `*A48*I0:${newSyncMode}*I1:${newSyncFormat}*I2:${newSyncRate}*Z`;
        this.sendCommand(command, "*A48*Z", (response) => {
            console.log("Set Sync Format Response:", response);
        });
    }

    // Enable/Disable LTC Callback
    LTCCallback(newLTCCallbackStatus) {
        if (newLTCCallbackStatus !== 0 && newLTCCallbackStatus !== 1) {
            console.error("Invalid LTC Callback Status: Must be 0 (Disable) or 1 (Enable).");
            return;
        }
        const command = `*A6*I0:${newLTCCallbackStatus}*Z`;
        
        this.sendCommand(command, "*A6*Z", (response) => {
            console.log("LTC Callback Response:", response);
        });
    }

    closeDevice() {
        if (this.unit) {
            try {
                this.unit.close();
                console.log("Device closed successfully.");
            } catch (err) {
                console.error("Error closing device:", err);
            }
        }
    }
};
