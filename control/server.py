
import requests
import json
import os

_BASE_URL = 'http://zachalambert.pythonanywhere.com/'
_AGENT_FILE = 'data/agent.json'


def make_get_request(url):
    full_url = _BASE_URL + url
    request = requests.get(full_url)
    if request.status_code!=200 and request.status_code!=201:
        return None
    else:
        return request.json()

def make_post_request(url, data):
    full_url = _BASE_URL + url
    request = requests.post(full_url, data=data)
    if request.status_code!=200 and request.status_code!=201:
        return None
    else:
        return request.json()

def get_agent():
    agent = None
    message = None 
    if os.path.exists(_AGENT_FILE):
        f = open(_AGENT_FILE, 'r')
        agent = json.load(f)
        id = agent['id']
        f.close()

        db_agent = make_get_request('agent/' + str(id))
        
        if db_agent==None:
            return None, 'Cannot connect to the server.'

        if agent!=db_agent:
            message = 'Local file is outdated. Updating.'
            f = open(_AGENT_FILE, 'w')
            f.write(json.dumps(db_agent))
            agent = db_agent 
        else:
            message = 'Local file is up to date'
    else:
        message = 'No local agent file found. Creating a new agent.'

        agent = make_post_request('new')

        if request.status_code != 200 and request.status_code != 201:
            return None, message + " Cannot connect to the server."

        json_string = json.dumps(agent)
        f = open(_AGENT_FILE, 'w')
        f.write(json_string)

    return agent, message


