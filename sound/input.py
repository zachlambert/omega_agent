#
# Copied from porcupine/demo/python/porcupine_demo_non_blocking.py 
#

import argparse
import os
import platform
import struct
import sys
import time
from datetime import datetime
from threading import Thread

import numpy as np
import pyaudio
import soundfile


PORCUPINE_PATH = '/home/pi/porcupine/'
sys.path.append(PORCUPINE_PATH + 'binding/python')
from porcupine import Porcupine


class ListenerConfig:

    def __init__(self):
        self.library_path = PORCUPINE_PATH + 'lib/raspberry-pi/arm11/libpv_porcupine.so'
        self.model_file_path = PORCUPINE_PATH + 'lib/common/porcupine_params.pv' 
        self.input_device_index = 2
        self.sensitivity = 0.5 


class Listener(Thread):

    def __init__(
            self,
            config,
            keyword_files,
            keyword_callback,
            phrase_keyword=None,
            phrase_callback=None,
            max_phrase_frames=400):

        super(Listener, self).__init__()
        self._config = config
        self._keyword_file_paths = [PORCUPINE_PATH + 'resources/keyword_files/raspberrypi/' +
                                    keyword_file for keyword_file in keyword_files]
        self._keyword_callback = keyword_callback

        if phrase_keyword is not None and phrase_callback is not None:
            self._phrase_keyword = phrase_keyword
            self._phrase_callback = phrase_callback
        else:
            self._phrase_keyword = None
            self._phrase_callback = None

        self._max_phrase_frames = max_phrase_frames
        self._output_path = 'data/phrase.wav'

    def run(self):
        num_keywords = len(self._keyword_file_paths)

        keyword_names = [os.path.basename(x).strip('.ppn').strip('_compressed').split('_')[0]
                         for x in self._keyword_file_paths]

        porcupine = None
        pa = None
        audio_stream = None
        sample_rate = None
        
        recording = False
        phrase_frames = []

        def _audio_callback(in_data, frame_count, time_info, status):
            nonlocal recording, phrase_frames

            if frame_count >= porcupine.frame_length:
                pcm = struct.unpack_from("h" * porcupine.frame_length, in_data)
                result = porcupine.process(pcm)
              
                keyword = None 
                if num_keywords == 1 and result:
                    keyword = keyword_names[0]
                elif num_keywords > 1 and result>=0:
                    keyword = keyword_names[result]
                
                if keyword is not None:
                    if self._phrase_keyword is not None and self._phrase_keyword==keyword:
                        if not recording:
                            print('Starting recording')
                            recording = True
                            phrase_frames = []
                        else:
                            print('Saving recording')
                            recording = False
                            self._save_recording(phrase_frames, sample_rate)
                    else:
                        self._keyword_callback(keyword)
                
                if recording:
                    phrase_frames.append(pcm)
                    if len(phrase_frames)>=self._max_phrase_frames:
                        recording = False
                        self._save_recording(phrase_frames, sample_rate)

            return None, pyaudio.paContinue

        try:
            porcupine = Porcupine(
                library_path=self._config.library_path,
                model_file_path=self._config.model_file_path,
                keyword_file_paths=self._keyword_file_paths,
                sensitivities=[self._config.sensitivity] * num_keywords)

            pa = pyaudio.PyAudio()
            sample_rate = porcupine.sample_rate
            num_channels = 1
            audio_format = pyaudio.paInt16
            frame_length = porcupine.frame_length

            audio_stream = pa.open(
                rate=sample_rate,
                channels=num_channels,
                format=audio_format,
                input=True,
                frames_per_buffer=frame_length,
                input_device_index=self._config.input_device_index,
                stream_callback=_audio_callback)

            audio_stream.start_stream()

            while True:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print('stopping ...')
        finally:
            if audio_stream is not None:
                audio_stream.stop_stream()
                audio_stream.close()

            if pa is not None:
                pa.terminate()

            if porcupine is not None:
                porcupine.delete()

    def _save_recording(self, phrase_frames, sample_rate):
        phrase_audio = np.concatenate(phrase_frames, axis=0).astype(np.int16)
        soundfile.write(self._output_path, phrase_audio, samplerate=sample_rate, subtype='PCM_16')
        self._phrase_callback(self._output_path) 

    _AUDIO_DEVICE_INFO_KEYS = ['index', 'name', 'defaultSampleRate', 'maxInputChannels']


if __name__ == '__main__':
    
    def process_keyword(keyword):
        print(keyword)
    def process_phrase(output_path):
        print('Saved audio at {}'.format(output_path))  
        os.system('aplay -f CD -Dplughw:1 {}'.format(output_path))

    config = ListenerConfig()

    listener = Listener(
        config=config,
        keyword_files=['blueberry_raspberrypi.ppn', 'grapefruit_raspberrypi.ppn'],
        keyword_callback=process_keyword,
        phrase_keyword='blueberry',
        phrase_callback=process_phrase)

    listener.run()
