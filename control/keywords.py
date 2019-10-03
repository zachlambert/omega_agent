
import os
import soundfile
import numpy as np

from sound.voice import speak


_recording = False
_start_index = 0

def _process_recording(recorded_frames, sample_rate):
    global _recording, _start_index
    if not _recording:
        _recording = True 
        _start_index = len(recorded_frames) - 1 
    else:
        _recording = False
        phrase_frames = recorded_frames[_start_index:]
        phrase_audio = np.concatenate(phrase_frames, axis=0).astype(np.int16)
        soundfile.write('data/temp.wav', phrase_audio, samplerate=sample_rate, subtype='PCM_16')
        os.system('aplay -f CD -Dplughw:1 data/temp.wav')

def _take_photo():
    speak('Taking a photo in 3. 2. 1.')
    # take photo


def process_keyword(keyword, recorded_frames, sample_rate):
    if keyword=='blueberry':
        _process_recording(recorded_frames, sample_rate)
    elif keyword=='grapefruit':
        _take_photo()


