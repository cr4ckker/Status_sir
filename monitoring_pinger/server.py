import os
from threading import Thread
from time import sleep, time

import requests, psutil
from uvicorn import run
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

from config import server_name, services
from models import Service

import extensions

app = FastAPI()

def flag(code: str):
    OFFSET = ord('🇦') - ord('A')
    if not code:
        return ''
    try:
        return ''.join([chr(ord(x) + OFFSET) for x in code.upper()])
    except ValueError:
        return ('\\U%08x\\U%08x' % (ord(x) + OFFSET for x in code.upper())).decode('unicode-escape')

def connect():
    sleep(3)
    if SERVER_HOST:
        print('Connecting to monitoring server')
        try:
            country_code = requests.get(f'https://geolocation-db.com/json/{ip}&position=true').json()['country_code']
            response = requests.post(SERVER_HOST+'/api/connect', json={'secret':SECRET_KEY, 'ip':ip, 'port':SERVER_PORT, 'name': flag(country_code) + ' ' + server_name, 'services':[service.name for service in services]})
            print(f'Monitoring server responsed: {response.text}')
        except requests.exceptions.ConnectionError:
            print('Monitoring server is not responding.')

@app.get('/logs/{service_name}')
async def get_logs(service_name: str):
    service: list[Service] = [service for service in services if service.name == service_name]
    if service: 
        return Response(service[0].get_logs())
    return Response('Service not found', status_code=400)

@app.post('/reboot')
async def reboot():
    try:
        return Response('OK')
    finally:
        os.system('reboot now')

@app.post('/healthcheck')
async def healthcheck():
    response = {
        'name': server_name,
        'status': 'Operational',
        'cpu': psutil.cpu_percent(),
        'ram': psutil.virtual_memory().percent,
        'services': {},
        'extra':{}
    }

    for service in services:
        is_active = service.check()
        response['services'][service.name] = 'Operational' if is_active else 'Critical'

    for _extension in extensions.store.extensions:
        _extension(response)

    return JSONResponse(response)

if __name__ == '__main__':
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY', 'SECRET')
    SERVER_PORT = os.getenv('SERVER_PORT', 7879)
    SERVER_HOST = os.getenv('SERVER_HOST', '')

    ip = requests.get('https://icanhazip.com').text.strip()

    Thread(target=connect).start()
    run(app, host='0.0.0.0', port=int(SERVER_PORT))