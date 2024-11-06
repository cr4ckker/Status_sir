import os, math
from threading import Thread
from time import sleep, time

import requests, psutil
from uvicorn import run
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

from config import server_name, services
from models import Service

app = FastAPI()

def connect():
    sleep(3)
    if SERVER_HOST:
        print('Connecting to monitoring server')
        try:
            response = requests.post(SERVER_HOST+'/api/connect', json={'secret':SECRET_KEY, 'ip':ip, 'port':SERVER_PORT, 'name':server_name, 'services':[service.name for service in services]})
            print(f'Monitoring server responsed: {response.text}')
        except requests.exceptions.ConnectionError:
            print('Monitoring server is not responding.')

@app.get('/logs/{service_name}')
async def get_logs(service_name: str):
    service: list[Service] = [service for service in services if service.name == service_name]
    if service: 
        return Response(service[0].get_logs())
    return Response('Service not found', status_code=400)

@app.post('/healthcheck')
async def healthcheck():
    response = {
        'name': server_name,
        'status': 'Operational',
        'cpu': psutil.cpu_percent(),
        'ram': psutil.virtual_memory().percent,
        'services': {}
    }
    for service in services:
        is_active = service.check()
        response['services'][service.name] = 'Operational' if is_active else 'Critical'
    return JSONResponse(response)

if __name__ == '__main__':
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY', 'SECRET')
    SERVER_PORT = os.getenv('SERVER_PORT', 7879)
    SERVER_HOST = os.getenv('SERVER_HOST', '')

    ip = requests.get('https://icanhazip.com').text.strip()

    Thread(target=connect).start()
    run(app, host=ip, port=int(SERVER_PORT))