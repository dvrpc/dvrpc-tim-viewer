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
                payload = self.queue.get()
                if payload is None:
                    con.commit()
                    break
                if "type" in payload:
                    self.process(con, payload)
                else:
                    self.log("Missing payload type")

    def process(self, con, payload):
        # Oh switch statement, where art thou?
        if   payload.type == TBL_NETOBJ:
            self.LoadAttributes(payload, con, True)
        elif payload.type == TBL_DATA:
            self.LoadAttributes(payload, con)
        elif payload.type == TBL_MATRIX:
            self.LoadMatrix(payload, con)
        elif payload.type == TBL_GEOMETRY:
            self.LoadGeometries(payload, con)
        else:
            print "Whoopsie"

    def LoadAttributes(self, payload, con, noTOD = False):
        if not noTOD:
            print payload.tod,
        print payload.netobj, payload.atts

    def LoadMatrix(self, payload, con):
        print payload.tod, payload.mtxno, payload.data.shape

    def LoadGeometries(self, payload, con):
        print payload.netobj, payload.att

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

class Utility:
    def __init__(self):
        pass
    @staticmethod
    def guessDType(field):
        pass