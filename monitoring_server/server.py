import os, math
from time import sleep, time
from traceback import print_exc

import requests
from uvicorn import run
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, Response
from dotenv import load_dotenv

import models
from models import extensions
from models import store, Server
from utils import jsonify_update
from db import DB

app = FastAPI()
static_files = APIRouter(prefix='/static')
api = APIRouter(prefix='/api')

@static_files.get('/js/{filename}')
def get_js_file(filename: str):
    with open(f'static/js/{filename}') as f:
        return Response(f.read())

@api.get('/logs/{service_id}')
async def get_logs(request: Request, service_id: str):
    event_data = {"method": request.method, "event": request.url.path, "body": {'service_id': service_id}}
    extensions.utils._process_extensions(event_data)

    server_id = service_id.split('.')[0]
    service_name = ''.join(service_id.split('.')[1::])
    server = Server(server_id)
    try:
        return server.get_logs(service_name)
    except requests.exceptions.ConnectionError:
        return Response('Connection error', status_code=500)
    
@api.post('/reboot/{server_id}')
async def reboot(request: Request, server_id: str):
    event_data = {"method": request.method, "event": request.url.path, "body": {'service_id': server_id}}
    extensions.utils._process_extensions(event_data)
    
    server = Server(server_id)
    try:
        return server.reboot()
    except requests.exceptions.ConnectionError:
        return Response('Connection error', status_code=500)

@app.get('/status')
async def status(request: Request):
    event_data = {"method": request.method, "event": request.url.path, "body": {}}
    extensions.utils._process_extensions(event_data)

    with open('templates/status.html') as f:
        return HTMLResponse(f.read())

@api.post('/status')
async def GetStatus(request: Request):
    total_report = {'servers':{},
                    'updates':{},
                    'timestamp':time()
                    }
    event_data = {"method": request.method, "event": request.url.path, "body": {'report':total_report}}
    extensions.utils._process_extensions(event_data)
    print(event_data)
    
    for server in store.db.get_servers():
        server_status = store.db.get_status(server.id, server.name)
        server_report = {'services': [],
                         'status': server_status,
                         'ip':server.ip,
                         'name': server.name,
                         'cpu':server.cpu if server_status != 'Critical' else 'Unknown',
                         'ram':server.ram if server_status != 'Critical' else 'Unknown',
                         'extra':server.extra if server_status != 'Critical' else {}
                         }
        for service_name in server.services:
            server_report['services'].append({ 'name':service_name, 'status':store.db.get_status(server.id, service_name) if server_status != 'Critical' else 'Unknown'} )
        total_report['servers'][server.id] = server_report
    
    for days_ago in range(7):
        day_time = (time() / 86400) - days_ago
        updates = store.db.execute('SELECT * FROM updates WHERE timestamp > ? AND timestamp < ? ORDER BY timestamp DESC', math.floor(day_time) * 86400, math.ceil(day_time) * 86400)
        key = str(math.floor(day_time) * 86400)
        total_report['updates'][key] = {}
        for update in updates:
            if update[1] not in total_report['updates'][key]:
                total_report['updates'][key][update[1]] = []
            total_report['updates'][key][update[1]].append(jsonify_update(update))
    return JSONResponse(total_report)

@api.post('/update')
async def AddUpdate(request: Request, update: models.req_update):
    event_data = {"method": request.method, "event": request.url.path, "body": update}
    extensions.utils._process_extensions(event_data)

    if SECRET_KEY != update.secret:
        return Response(status_code=403)
    store.db.add_update(update.service_name, update.server_id, update.status, update.title, update.text)
    return Response('OK')

@api.post('/connect')
async def AddServer(request: Request, server: models.req_server):
    event_data = {"method": request.method, "event": request.url.path, "body": server}
    extensions.utils._process_extensions(event_data)

    try:
        if SECRET_KEY != server.secret:
            return Response(status_code=403)
        response = requests.post('http://%s:%s/healthcheck' % (server.ip, server.port), json={'timestamp':time()}, timeout=5)
        if response.status_code != 200:
            return Response('Failed callback', status_code=400)
        store.db.add_server(server)
        return Response('OK')
    except:
        print_exc()
        return Response('Failed', status_code=400)

@api.post('/remove/{server_id}')
async def RemoveServer(request: Request, server_id: str):
    store.db.remove_server(server_id)
    return Response('OK')

if __name__ == '__main__':
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY', 'SECRET')
    SERVER_PORT = os.getenv('SERVER_PORT', 7878)

    store.db = DB('data.db')
    app.include_router(static_files)
    app.include_router(api)
    ip = requests.get('https://ipv4.icanhazip.com').text.strip()
    run(app, host='0.0.0.0', port=int(SERVER_PORT))