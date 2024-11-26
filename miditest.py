import mido

timecode = {
    'frames': 0,
    'seconds': 0,
    'minutes': 0,
    'hours': 0,
    'fps': 0
}

frame_rates = {
    0: 24,
    1: 25,
    2: 29.97,
    3: 30,
}

def change_to_SMPTE(msg):
    if msg.type == "quarter_frame":
        frame_type = msg.frame_type
        frame_value = msg.frame_value
        
        if frame_type == 0:
            timecode['frames'] = (timecode['frames'] & 0xF0) | frame_value
            
        elif frame_type == 1:
            timecode['frames'] = (timecode['frames'] & 0x0F) | (frame_value << 4)
            
        elif frame_type == 2:
            timecode['seconds'] = (timecode['seconds'] & 0xF0) | frame_value
            
        elif frame_type == 3:
            timecode['seconds'] = (timecode['seconds'] & 0x0F) | (frame_value << 4)
            
        elif frame_type == 4:
            timecode['minutes'] = (timecode['minutes'] & 0xF0) | frame_value
            
        elif frame_type == 5:
            timecode['minutes'] = (timecode['minutes'] & 0x0F) | (frame_value << 4)
            
        elif frame_type == 6:
            timecode['hours'] = (timecode['hours'] & 0xF0) | frame_value
            
        elif frame_type == 7:
            timecode['hours'] = (timecode['hours'] & 0x0F) | ((frame_value & 0x01) << 4)
            timecode['fps'] = (frame_value >> 1) & 0x03
    
        display_timecode()
            
def display_timecode():
    frame_rate = frame_rates.get(timecode['fps'], 'Unknown')
    print(f"Timecode in HH:MM:SS:FF format: {timecode['hours']:02}:{timecode['minutes']:02}:{timecode['seconds']:02}:{timecode['frames']:02} @ {frame_rate} fps")
    
with mido.open_input('Ambient Device 0') as port:
    for msg in port:
        print(msg)
        print(change_to_SMPTE(msg))
        
