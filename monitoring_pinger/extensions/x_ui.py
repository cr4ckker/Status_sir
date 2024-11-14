# This is a real example of an extension that enriches response with data from 3x-ui

from time import time
from json import load

from requests import post, Session

from .utils import extension, when_service_is_up

class X_UI_API: 
    def __init__(self, config) -> None:
        self.username = config['username']
        self.password = config['password']
        self.port = config['port']
        self.webbasepath = config['webbasepath']
        self.host = "http://localhost:%s/%s" % (self.port, self.webbasepath)
        self.connect()

    def _post(self, method, data = {}):
        self.update_session()
        print(self.host + method)
        print(data)
        _response = self.session.post(self.host + method, data=data, headers={'Accept':'application/json, text/plain, */*'}, verify=False)
        print(_response.status_code)
        print(_response.text)
        return _response

    def connect(self):
        self.session = Session()
        self.session_expiration = time() + 3500
        self._post('/login', {'username':self.username, 'password':self.password})

    def update_session(self):
        if self.session_expiration < time():
            self.connect()
    
    def get_list(self, filter = {}):
        inbounds = self._post('/panel/inbound/list').json().get('obj', [])
        inbounds = inbounds if inbounds else []
        return [inbound for inbound in inbounds if all([inbound.get(key) == value for key, value in filter.items()])]
    
    def get_online(self):
        online = self._post('/panel/inbound/onlines').json().get('obj', [])
        return len(online if online else [])


x_ui_config_path = '/etc/status/config/x_ui.json'
with open(x_ui_config_path) as f:
    config = load(f)

x_ui_api = X_UI_API(config)

@extension # Marks a function as an extension
@when_service_is_up('x-ui') # Enriches the response only if the service has status "Operational"
def check_3xui(response: dict) -> dict:
    total = len(x_ui_api.get_list())
    online = x_ui_api.get_online()
    response['extra']['x-ui'] = {'total':total, 'online':online}