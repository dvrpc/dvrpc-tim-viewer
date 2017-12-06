import threading

import psycopg2 as psql

import time

TBL_GEOMETRY = "geom"
TBL_NETOBJ = "net"
TBL_MATRIX = "mtx"
TBL_DATA = "dat"

class Database(threading.Thread):
    def __init__(self, db_credentials, queue):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
        self.queue = queue

    def run(self):
        with psql.connect(**self.db_credentials) as con:
            while True:
                payload = self.queue.get()
                if payload is None:
                    break

                if "type" in payload:
                    self.process(con, payload)
                else:
                    self.log("Missing payload type")

                time.sleep(0.1)

    def process(self, con, payload):
        cur = con.cursor()
        # cur.execute("SELECT COUNT(*) FROM mtx_210_am")
        # (cnt,) = cur.fetchone()
        # print "OK", cnt
        print payload.type, payload.tod, payload.netobj, payload.att

    @classmethod
    def log(self, message):
        print "Database:", message

class Echo(threading.Thread):
    def __init__(self, queue):
        super(Echo, self).__init__()
        self.queue = queue
    def run(self):
        while True:
            payload = self.queue.get()
            print payload