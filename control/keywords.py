
import os
import soundfile
import numpy as np

from sound.voice import speak


_recording = False
_phrase_frames = []
_MAX_FRAMES = 300 
SAMPLE_RATE = 0

def _save_recording():
    if SAMPLE_RATE==0:
        print('Sample rate has not been set')
        return
    phrase_audio = np.concatenate(_phrase_frames, axis=0).astype(np.int16)
    soundfile.write('data/temp.wav', phrase_audio, samplerate=SAMPLE_RATE, subtype='PCM_16')
    os.system('aplay -f CD -Dplughw:1 data/temp.wav')
 
def _process_recording():
    global _recording, _phrase_frames 
    if not _recording:
        _recording = True 
        _phrase_frames = []
    else:
        _recording = False
        _save_recording()

def _take_photo():
    speak('Taking a photo in 3. 2. 1.')
    # take photo

def process_frame(pcm):
    global _recording, _phrase_frames
    if _recording:
        _phrase_frames.append(pcm)
        if len(_phrase_frames)>=_MAX_FRAMES:
            speak('Max phrase length reached, stopping recording.')
            _recording = False
            _save_recording()

def process_keyword(keyword):
    if keyword=='blueberry':
        _process_recording()
    elif keyword=='grapefruit':
        _take_photo()


