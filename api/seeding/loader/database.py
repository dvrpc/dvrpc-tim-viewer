import threading

import psycopg2 as psql

TBL_GEOMETRY = "geom"
TBL_DATA = "net"
TBL_MATRIX = "mtx"

class Database(threading.Thread):
    def __init__(self, db_credentials, queue):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
        self.queue = queue

    def run(self):
        with psql.connect(**self.db_credentials) as con:
            while True:
                payload = self.queue.get()
                if "cmd" in payload:
                    if payload["cmd"] == "exit":
                        break
                else:
                    self.process(con, payload)

    def process(self, con, payload):
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM mtx_210_am")
        (cnt,) = cur.fetchone()
        print "OK", cnt

class Echo(threading.Thread):
    def __init__(self, queue):
        super(Echo, self).__init__()
        self.queue = queue
    def run(self):
        while True:
            payload = self.queue.get()
            print payload