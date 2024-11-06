from time import sleep, time
from traceback import print_exc

import config
from db import DB, Server, store


def pinger():
    next_update = time()

    while True:
        if next_update > time():
            sleep(next_update - time())
        next_update += config.PING_INTERVAL
        print(f'Check started {time()}')
        for server in store.db.get_servers():
            try:
                server.ping()
            except ConnectionError:
                store.db.add_update(server.name, server.id, 'Critical', f'Сервер {server.name} не отвечает', 'Ошибка соединения с сервером при отправке пинга.')
            except Exception as e:
                print_exc()
        print(f'Check ended {time()}')

if __name__ == '__main__':
    store.db = DB('data.db')
    pinger()