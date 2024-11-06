import os, math
from time import sleep, time
from traceback import print_exc

import requests
from uvicorn import run
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, Response
from dotenv import load_dotenv

import models
from models import store, Server
from utils import jsonify_update
from db import DB

app = FastAPI()
static_files = APIRouter(prefix='/static')

@static_files.get('/js/{filename}')
def get_js_file(filename: str):
    with open(f'static/js/{filename}') as f:
        return Response(f.read())

@app.get('/api/logs/{service_id}')
async def get_logs(service_id):
    server_id = service_id.split('.')[0]
    service_name = ''.join(service_id.split('.')[1::])
    server = Server(server_id)
    try:
        return server.get_logs(service_name)
    except requests.exceptions.ConnectionError:
        return Response('Connection error to server', status_code=500)

@app.get('/status')
async def status():
    with open('templates/status.html') as f:
        return HTMLResponse(f.read())

@app.post('/api/status')
async def GetStatus():
    total_report = {'servers':{},
                    'updates':{},
                    'timestamp':time()
                    }
    for server in store.db.get_servers():
        server_status = store.db.get_status(server.id, server.name)
        server_report = {'services': [],
                         'status': server_status,
                         'ip':server.ip,
                         'name': server.name,
                         'cpu':server.cpu,
                         'ram':server.ram
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

@app.post('/api/update')
async def AddUpdate(request: Request, update: models.req_update):
    if SECRET_KEY != update.secret:
        return Response(status_code=403)
    store.db.add_update(update.service_name, update.server_id, update.status, update.title, update.text)
    return Response('OK')

@app.post('/api/connect')
async def AddServer(request: Request, server: models.req_server):
    try:
        if SECRET_KEY != server.secret:
            return Response(status_code=403)
        response = requests.post('http://%s:%s/healthcheck' % (server.ip, server.port), timeout=5)
        if response.status_code != 200:
            return Response('Failed callback', status_code=400)
        store.db.add_server(server)
        return Response('OK')
    except:
        print_exc()
        return Response('Failed', status_code=400)

@app.post('/api/remove')
async def RemoveServer(request: Request, ip: str):
    store.db.remove_server(ip)
    return Response('OK')

if __name__ == '__main__':
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY', 'SECRET')
    SERVER_PORT = os.getenv('SERVER_PORT', 7878)

    store.db = DB('data.db')
    app.include_router(static_files)
    ip = requests.get('https://icanhazip.com').text.strip()
    run(app, host='0.0.0.0', port=int(SERVER_PORT))