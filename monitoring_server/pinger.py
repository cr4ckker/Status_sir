from queue import Queue
from threading import Thread
from time import sleep, time
from datetime import datetime
from traceback import print_exc

import config
from db import DB, Server, store
from models import extensions

def worker():
    while True:
        try:
            server, check_num = store.check_queue.get()
            if server and store.check_num <= check_num:
                server.ping(check_num)
        except:
            print_exc()
            print('ping error')

def Check_servers():
    print(f'[ {datetime.now():%H:%M:%S} ] Check #{store.check_num} started')
    for server in store.db.get_servers():
        if server.id not in store.last_updates:
            store.last_updates[server.id] = store.check_num
        store.check_queue.put((server, store.check_num))

def Pinger():
    while True:
        if time() // config.PING_INTERVAL > store.check_num:
            store.check_num = int(time() // config.PING_INTERVAL)
            Thread(target=Check_servers, daemon=True).start()
        sleep(0.05)

if __name__ == '__main__':
    store.check_num = 0
    store.last_updates = {}
    store.check_queue = Queue()
    store.db = DB('data.db')

    workers = [Thread(target=worker) for _ in range(50)]
    [t.start() for t in workers]
    Pinger()