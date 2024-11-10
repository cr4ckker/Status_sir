import time
from json import dumps
from sqlite3 import connect
from uuid import uuid1

from models import store, Server, req_server


class DB: 
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_tables()

    def initialize_tables(self):
        self.execute('''CREATE TABLE IF NOT EXISTS updates (
                     id TEXT PRIMARY KEY,
                     server_id TEXT,
                     service_name TEXT,
                     severity TEXT,
                     title TEXT,
                     text TEXT,
                     cpu REAL,
                     ram REAL,
                     timestamp INTEGER
                     );''')
        self.execute('''CREATE TABLE IF NOT EXISTS servers (
                     id TEXT PRIMARY KEY UNIQUE,
                     ip TEXT,
                     port TEXT,
                     name TEXT,
                     services TEXT
                     );''')

    def get_servers(self):
        servers = self.execute('SELECT id FROM servers ORDER BY "_rowid_" ASC;')

        for server in servers:
            yield Server(server[0])

    def get_status(self, server_id, service_name):
        status = self.execute('SELECT severity FROM updates WHERE server_id = ? AND service_name = ? ORDER BY timestamp DESC;', server_id, service_name, fetchone=True)
        return status[0] if status else 'Operational'

    def add_server(self, server: req_server):
        uid = str(uuid1())
        db_info = self.execute('SELECT id FROM servers WHERE ip = ? AND port = ?', server.ip, server.port, fetchone=True)
        if db_info:
            self.execute('UPDATE servers SET name = ?, services = ? WHERE id = ?', server.name, dumps(server.services), db_info[0])
        else:
            self.execute('INSERT INTO servers VALUES (?, ?, ?, ?, ?, ?, ?)', uid, server.ip, server.port, server.name, dumps(server.services), 0, 0)
        return uid

    def server_update(self, server_id, cpu, ram):
        self.execute("UPDATE servers SET cpu = ?, ram = ? WHERE id = ?", cpu, ram, server_id)

    def remove_server(self, ip: str):
        self.execute("DELETE FROM servers WHERE ip = ?", ip)

    def add_update(self, service_name: str, server_id: str, severity: str, title: str, text: str = ''):
        result = self.execute('INSERT INTO updates VALUES (?, ?, ?, ?, ?, ?, ?)', str(uuid1()), server_id, service_name, severity, title, text, int(time.time()))
        return result

    def execute(self, sql_query: str, *params, fetchone = False):
        result = None
        with connect(self.db_path) as db:
            cursor = db.cursor()
            cursor = cursor.execute(sql_query, params)
            if sql_query.startswith('SELECT'):
                result = cursor.fetchone() if fetchone else cursor.fetchall()
            db.commit()
        return result