import requests.exceptions
from json import loads
from requests import get, post
from time import time

from datetime import datetime
from pydantic import BaseModel

status_messages = {
    'Critical': '%s не отвечает',
    'Warning': '%s',
    'Operational': '%s восстановлен',
    'Maintenance': 'На %s начаты технические работы',
}

class store:
    last_updates = {}
    servers = {}

class Server:
    __slots = ['id', 'ip', 'port', 'name', 'services', 'cpu', 'ram']
    __json_vars = ['services']

    def __init__(self, id):
        self.id = id
        data = store.db.execute('SELECT * FROM servers WHERE id = ?', self.id, fetchone=True)
        self.load(*data)
    
    def load(self, *args):
        if args:
            for i, slot in enumerate(self.__slots):
                setattr(self, slot, loads(args[i]) if slot in self.__json_vars else args[i])

    def get_logs(self, service):
        return get('http://%s:%s/logs/%s' % (self.ip, self.port, service)).text
            
    def ping(self, check_num: int = 1e10):
        print(f'[ {datetime.now():%H:%M:%S} ] {'[ %s ]' % self.name:<35} Checking')
        store.last_updates[self.id] = max(check_num, store.last_updates.get(self.id, 0))
        for attempt in range(4):
            try:
                response = post('http://%s:%s/healthcheck' % (self.ip, self.port), json={'timestamp':time()}, timeout=15)
                response_data = response.json()
                server_status = response_data['status']
                break
            except requests.exceptions.ConnectionError: 
                if attempt == 3:
                    server_status = 'Critical'
                    print(f'[ {datetime.now():%H:%M:%S} ] {'[ %s ]' % self.name:<35} Not responding #{attempt} Attempt( {'Actual' if store.last_updates[self.id] <= check_num else 'Obsolete'}\t#{check_num})')
        if server_status != store.db.get_status(self.id, self.name) and store.last_updates[self.id] <= check_num:
            store.db.add_update(self.name, self.id, server_status, self.name, status_messages[server_status] % self.name)
        
        store.db.server_update(self.id, response_data['cpu'], response_data['ram'])
        for service in response_data['services']:
            store.last_updates[service] = max(check_num, store.last_updates.get(service, 0))
            service_status = store.db.get_status(self.id, service)
            new_status = response_data['services'][service]
            if service_status != new_status and store.last_updates[service] <= check_num:
                store.db.add_update(service, self.id, new_status, service, status_messages[new_status] % service)
            print(f'[ {datetime.now():%H:%M:%S} ] {'[ %s ]' % self.name:<35} Service {'%s:' % service:<20} {new_status:<15} ( {'Actual' if store.last_updates[service] <= check_num else 'Obsolete'}\t#{check_num})')
                
class req_server(BaseModel):
    secret: str
    ip: str
    port: int
    name: str
    services: list

class req_update(BaseModel):
    secret: str
    service_name: str
    server_id: str
    status: str
    title: str
    text: str = ''