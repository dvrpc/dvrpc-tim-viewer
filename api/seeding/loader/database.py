import threading

import psycopg2 as psql

import time

# TOD agnostic
TBL_NETOBJ = "net"
# TOD dependent
TBL_DATA = "dat"
# TOD dependent
TBL_MATRIX = "mtx"
# TOD agnostic(?)
TBL_GEOMETRY = "geom"

class Database(threading.Thread):
    def __init__(self, db_credentials, queue):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
        self.queue = queue

    def run(self):
        with psql.connect(**self.db_credentials) as con:
            while True:
                print self.queue.qsize(), 
                payload = self.queue.get()
                if payload is None:
                    con.commit()
                    break
                if "type" in payload:
                    self.process(con, payload)
                else:
                    self.log("Missing payload type")
                time.sleep(0.1)

    def process(self, con, payload):
        cur = con.cursor()
        print payload.type, payload.tod, payload.netobj, payload.atts
        print '\t', payload.data[0] if len(payload.data) > 0 else None

    def LoadMatrixData(self):
        pass
    def InsertMatrixData(self):
        f = StringIO.StringIO()
        w = csv.writer(f)
        w.writerows(mtx_listing[numpy.where(mtx_listing[:,2] < 1e5)])
        f.seek(0)
        cur.copy_from(
            f,
            tblname,
            columns = [
                "oindex",
                "dindex",
                "val"
            ],
            sep = ','
        )
        f.close()

    @classmethod
    def log(self, message):
        print "Database:", message