
import requests
import json
import os
import datetime
import time

from control.chat import introduce_yourself
from control.process import process_keyword, process_phrase
from control.server import get_agent
from sound.input import ListenerConfig, Listener 
from sound.output import speak


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

config = ListenerConfig()

listener = Listener(
    config=config,
    keyword_files=['blueberry_raspberrypi.ppn', 'grapefruit_raspberrypi.ppn'],
    keyword_callback=process_keyword,
    phrase_keyword='blueberry',
    phrase_callback=process_phrase)

listener.run()
