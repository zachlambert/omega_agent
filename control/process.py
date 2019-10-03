
import os

from sound.output import speak


def _take_photo():
    speak('Taking a photo in 3. 2. 1.')
    'todo'

def process_keyword(keyword):
    if keyword=='grapefruit':
        _take_photo()

def process_phrase(output_path):
    speak('Phrase recorded, playing back.')
    os.system('aplay -f CD -Dplughw:1 {}'.format(output_path))
 
