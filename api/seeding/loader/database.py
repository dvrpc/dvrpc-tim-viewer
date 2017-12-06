import csv
import StringIO
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

TBL_NAMETMPLT_NETOBJ = "net_{netobj}"
TBL_NAMETMPLT_MTX = "mtx_{mtxno}_{tod}"
TBL_NAMETMPLT_DATA = "dat_{netobj}_{tod}"
TBL_NAMETMPLT_GEOMETRY = "geom_{netobj}"

"CREATE TABLE {tblname} ({fields})"
"ALTER TABLE {tblname} ADD COLUMN ({fname} {dtype})"
"INSERT INTO {tblname} VALUES ({nargs})"

class Database(threading.Thread):
    MTX_DEFAULT_COLUMNS = ["oindex", "dindex", "val"]
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
        f = self._bufferMatrix(payload.data)
        tblname = TBL_NAMETMPLT_MTX.format(**{'mtxno': payload.mtxno, 'tod': payload.tod})
        cur = con.cursor()
        cur.copy_from(
            f,
            tblname,
            columns = self.MTX_DEFAULT_COLUMNS,
            sep = ','
        )
        f.close()
        con.commit()

    def _bufferMatrix(self, mtx_listing):
        f = StringIO.StringIO()
        w = csv.writer(io)
        w.writerows(mtx_listing)
        f.seek(0)
        return f

    def LoadGeometries(self, payload, con):
        print payload.netobj, payload.att
        "ST_GeomFromEWKT('{wkt}')".format(**{"wkt": })
        

    @classmethod
    def log(self, message):
        print "Database:", message

class Utility:
    def __init__(self):
        pass
    @staticmethod
    def guessDType(field):
        pass