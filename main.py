
import requests
import json
import os
import datetime
import time

from control.chat import introduce_yourself
from control.keywords import process_keyword, process_frame
from control.server import get_agent
from sound.keyword_detector import KeywordDetector
from sound.voice import speak

""
CONNECTION_MAX_TRIES = 3

agent = None
tries = 0
while agent==None:
    agent, message = get_agent()
    speak(message)
    if agent==None:
        tries += 1
        if tries<CONNECTION_MAX_TRIES:
            speak('Will retry in 5 seconds')
            time.sleep(5)
        else:
            speak('Unable to connect after {} attempts'.format(tries))
            speak('Exiting program')
            exit()


introduce_yourself(agent)
speak('Starting the listening process')
"""
keyword_detector = KeywordDetector(
    keyword_callback=process_keyword,
    keyword_files=['blueberry_raspberrypi.ppn',
                   'grapefruit_raspberrypi.ppn'],
    input_device_index=2,
    sensitivity=0.5,
    process_frame=process_frame)

keyword_detector.run()
