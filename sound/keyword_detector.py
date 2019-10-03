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


_LIBRARY_PATH = PORCUPINE_PATH + 'lib/raspberry-pi/arm11/libpv_porcupine.so'
_MODEL_FILE_PATH = PORCUPINE_PATH + 'lib/common/porcupine_params.pv'

class KeywordDetector(Thread):

    def __init__(
            self,
            keyword_callback,
            keyword_files,
            input_device_index=2,
            sensitivity=0.5,
            output_path=None):

        super(KeywordDetector, self).__init__()

        self._library_path = _LIBRARY_PATH
        self._model_file_path = _MODEL_FILE_PATH 
      
        self._keyword_callback = keyword_callback

        self._keyword_file_paths = [PORCUPINE_PATH + 'resources/keyword_files/raspberrypi/' +
                                    keyword_file for keyword_file in keyword_files]
        self._input_device_index = input_device_index
        self._sensitivity = float(sensitivity)

        self._output_path = output_path
        
        self._recorded_frames = []

    def run(self):
        num_keywords = len(self._keyword_file_paths)

        keyword_names =\
            [os.path.basename(x).strip('.ppn').strip('_compressed').split('_')[0] for x in self._keyword_file_paths]

        porcupine = None
        pa = None
        audio_stream = None
        sample_rate = None

        def _audio_callback(in_data, frame_count, time_info, status):
            if frame_count >= porcupine.frame_length:
                pcm = struct.unpack_from("h" * porcupine.frame_length, in_data)
                result = porcupine.process(pcm)

                self._recorded_frames.append(pcm)
 
                if num_keywords == 1 and result:
                    self._keyword_callback(keyword_names[0], self._recorded_frames, sample_rate)
                elif num_keywords > 1 and result>=0:
                    self._keyword_callback(keyword_names[result], self._recorded_frames, sample_rate)
           
            return None, pyaudio.paContinue

        try:
            porcupine = Porcupine(
                library_path=self._library_path,
                model_file_path=self._model_file_path,
                keyword_file_paths=self._keyword_file_paths,
                sensitivities=[self._sensitivity] * num_keywords)

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
                input_device_index=self._input_device_index,
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

            if self._output_path is not None and sample_rate is not None and len(self._recorded_frames) > 0:
                recorded_audio = np.concatenate(self._recorded_frames, axis=0).astype(np.int16)
                soundfile.write(self._output_path, recorded_audio, samplerate=sample_rate, subtype='PCM_16')

    _AUDIO_DEVICE_INFO_KEYS = ['index', 'name', 'defaultSampleRate', 'maxInputChannels']


if __name__ == '__main__':
    
    def example_callback(keyword):
        print(keyword)

    keyword_detector = KeywordDetector(
        keyword_callback = example_callback,
        keyword_files=['blueberry_raspberrypi.ppn'],
        input_device_index=2,
        sensitivity=0.5)

    keyword_detector.run()
