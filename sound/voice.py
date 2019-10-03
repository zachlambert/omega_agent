import os

def speak(text, amplitude=20):
    os.system('espeak "{}" --stdout -a {}|aplay -Dplughw:1'.format(text, amplitude))

if __name__=='__main__':
    speak('Hello, can you hear me?')
