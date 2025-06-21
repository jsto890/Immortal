#!/usr/bin/env python3

# Requires hidapi (https://pypi.org/project/hidapi)

# This sample code is meant to demonstrate a very basic communication
# with an Ambient ACN-CL ("Lockit") device over USB-HID.
#
# Please be aware that this script is far from production-ready and contains
# the following limitations at least:
# - Error handling is missing.
# - A single "read" call is not guaranteed to return a complete server
#   message (even if it is less than 64 bytes long).
# - The result of a single "read" call might contain multiple server messages.
# - The protocol is not strictly "command-response". There are also
#   notification messages sent asynchronously by the server. So reading a
#   message right after sending a command is not guaranteed to be the
#   corresponding response message. However, response messages are guaranteed
#   to be in the same order as the request messages sent by the client.

# Script can now handle multiple response messages in a single read call 
# while being accurate, just need to add in what response you want aswell as the tag.
# When recieving the timecode, it seems like the values extracted are wrong or the conversion is wrong.

import hid
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import HID_VENDOR_ID, HID_PRODUCT_ID, CONFIG_NOTE

def send_recv(h, msg, tag):
    assert len(msg) <= 64

    # We always write 65 bytes using HID-API:
    # - first byte identifies the endpoint (not part of the payload)
    # - zero-pad msg to 64-byte payload
    pad_len = 64 - len(msg)
    packet = bytes(1) + msg + bytes(pad_len)
    h.write(packet)

    while True:
        res = h.read(64)
        if res:
            res_end = 65
            try:
                res_end = res.index(0)
            except:
                pass
            
            response = bytes(res[0:res_end])
            if response.startswith(tag):
                return response
            
def parse_ltc_response(msg):
    msg_str = msg.decode()
    raw_ltc = msg_str.split("*I0:")[1].split("*")[0]
    fps = int(msg_str.split("*I1:")[1].split("*")[0])
    
    raw_ltc_bin = bin(int(raw_ltc, 16))[2:].zfill(64)   
    
    frames_units = int(raw_ltc_bin[0:4], 2)
    frames_tens = int(raw_ltc_bin[8:10], 2)
    frames = frames_units + (frames_tens * 10)
    
    seconds_units = int(raw_ltc_bin[16:20], 2)
    seconds_tens = int(raw_ltc_bin[24:27], 2)
    seconds = seconds_units + (seconds_tens * 10)
    
    minutes_units = int(raw_ltc_bin[32:36], 2)
    minutes_tens = int(raw_ltc_bin[40:43], 2)
    minutes = minutes_units + (minutes_tens * 10)
    
    hours_units = int(raw_ltc_bin[48:52], 2)
    hours_tens = int(raw_ltc_bin[56:58], 2)
    hours = hours_units + (hours_tens * 10)
    
    timecode = f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02} @ {fps} fps"
    return timecode
                

# Replace hardcoded device IDs with config values
AMBIENT_USB_VENDOR = HID_VENDOR_ID
ACN_CL_USB_PRODUCT = HID_PRODUCT_ID

h = hid.device()
h.open(AMBIENT_USB_VENDOR, ACN_CL_USB_PRODUCT)

print("Connecting to Lockit with S/N: %s" % h.get_serial_number_string())

firmware_tag = b"*A0*" #Firmware Tag
LTC_tag = b"*A6*I0:1*" #Enable LTC  Callback Tag, NEED TO FIND RIGHT INSTRUCTION CODE, ONE ON SHEET IS WRONG
RTC_tag = b"*A64*" #RTC Tag
TC_tag = b"*Q35*" #TC Tag

res = send_recv(h, LTC_tag + b"Z", LTC_tag)
print(f"LTC response: {res.decode()}")
ltc_timecode = parse_ltc_response(res)
print(f"Converted LTC timecode: {ltc_timecode}")

res = send_recv(h, RTC_tag + b"Z", RTC_tag)
print("Regular Timecode response: %s" % res.decode())

res = send_recv(h, TC_tag + b"Z", TC_tag)
print("Timecode response: %s" % res.decode())