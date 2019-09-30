import requests
import json
import os
import datetime


base_url = 'http://zachalambert.pythonanywhere.com/'
agent_json_file = 'agent.json'

agent = None
if os.path.exists(agent_json_file):
    f = open(agent_json_file, 'r')
    agent = json.load(f)
    id = agent['id']
    f.close()

    GET_URL = base_url + 'agent/' + str(id)
    request = requests.get(GET_URL)
    if request.status_code != 200 and request.status_code != 201:
        raise Exception('Request returned error')
    
    db_agent = request.json()
    if agent!=db_agent:
        print('Updating agent file')
        f = open(agent_json_file, 'w')
        f.write(json.dumps(db_agent))
        agent = db_agent 
    else:
        print('Local file is up to date')
else:
    print('No local agent file, creating new')

    NEW_URL = base_url + 'new'
    request = requests.post(url=NEW_URL)
    agent = request.json()

    json_string = json.dumps(agent)
    f = open(agent_json_file, 'w')
    f.write(json_string)

now = datetime.datetime.now()
birth = datetime.datetime.strptime(agent['birth_date'], '%Y-%m-%dT%H:%M:%SZ')
delta = now - birth

print('Hello, my name is {}. My id number is {} and I am {} seconds old.'.format(agent['name'], agent['id'], delta.seconds))
