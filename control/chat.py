
import datetime

from sound.output import speak


def introduce_yourself(agent):
    now = datetime.datetime.now()
    birth = datetime.datetime.strptime(agent['birth_date'], '%Y-%m-%dT%H:%M:%SZ')
    delta = now - birth

    speak('Hello, my name is {}. My id number is {} and I am {} seconds old.'
          .format(agent['name'], agent['id'], delta.seconds))


