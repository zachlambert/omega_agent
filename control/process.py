
import os
import time

from picamera import PiCamera

from sound.output import speak
from control.server import send_image, send_phrase
camera = PiCamera()

def _take_photo():
    file_path = 'data/image.png'
    speak('Taking a photo in 3. 2. 1.')
    camera.start_preview()
    time.sleep(2)
    camera.capture(file_path)
    camera.stop_preview()
    speak('Photo taken.')
    result = send_image(file_path) 
    if 'message' in result:
        speak(result['message'])
    else:
        speak('Error occurred when sending image to server.')

def process_keyword(keyword):
    if keyword=='grapefruit':
        _take_photo()

def process_phrase(file_path):
    speak('Phrase recorded, playing back.')
    os.system('aplay -f CD -Dplughw:1 {}'.format(file_path))
    result = send_phrase(file_path) 
    if 'message' in result:
        speak(result['message'])
    else:
        speak('Error occurred when sending phrase to server.')
