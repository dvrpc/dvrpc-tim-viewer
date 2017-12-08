# Note:
# All data processing should take place in Visum.py
# Only database-specific processing should be here
# e.g. PostGIS overhead

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

SQL_CREATE_TBL_MTX = "CREATE TABLE IF NOT EXISTS {0} (oindex smallint, dindex smallint, val double precision);"
SQL_CREATE_IDX_MTX_O = "CREATE INDEX IF NOT EXISTS {0}_o_idx ON public.{0} (oindex ASC NULLS LAST);"
SQL_CREATE_IDX_MTX_D = "CREATE INDEX IF NOT EXISTS {0}_d_idx ON public.{0} (dindex ASC NULLS LAST);"

class Database(threading.Thread):
    MTX_DEFAULT_COLUMNS = ["oindex", "dindex", "val"]
    def __init__(self, db_credentials, queue):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
        self.queue = queue
        self.con = None

    def run(self):
        with psql.connect(**self.db_credentials) as con:
            self.con = con
            while True:
                payload = self.queue.get()
                if payload is None:
                    con.commit()
                    break
                if "type" in payload:
                    self.process(payload)
                else:
                    self.log("Missing payload type")

    def process(self, payload):
        # Oh switch statement, where art thou?
        if   payload.type == TBL_NETOBJ:
            self.LoadAttributes(payload, True)
        elif payload.type == TBL_DATA:
            self.LoadAttributes(payload)
        elif payload.type == TBL_MATRIX:
            self.LoadMatrix(payload)
        elif payload.type == TBL_GEOMETRY:
            self.LoadGeometries(payload)
        else:
            print "Whoopsie"

    def LoadAttributes(self, payload, noTOD = False):
        if noTOD:
            tblname = TBL_NAMETMPLT_NETOBJ.format(**{'netobj':payload.netobj})
        else:
            tblname = TBL_NAMETMPLT_DATA.format(**{'netobj':payload.netobj,'tod':payload.tod})
        print Utility.formatCreate(tblname, payload.atts)
        for row in payload.data:
            print Utility.formatInsert(self.con, tblname, row, payload.atts)
            break

    def LoadMatrix(self, payload):
        f = self._bufferMatrix(payload.data)
        tblname = TBL_NAMETMPLT_MTX.format(**{'mtxno': payload.mtxno, 'tod': payload.tod})
        cur = self.con.cursor()
        cur.execute(SQL_CREATE_TBL_MTX.format(tblname))
        cur.copy_from(
            f,
            tblname,
            columns = self.MTX_DEFAULT_COLUMNS,
            sep = ','
        )
        f.close()
        cur.execute(SQL_CREATE_IDX_MTX_O.format(tblname))
        cur.execute(SQL_CREATE_IDX_MTX_D.format(tblname))
        self.con.commit()

    def _bufferMatrix(self, mtx_listing):
        f = StringIO.StringIO()
        w = csv.writer(f)
        w.writerows(mtx_listing)
        f.seek(0)
        return f

    def LoadGeometries(self, payload):
        # Create temporary table for model SRID
        # Reproject the data into a permanent table via internal Postgis
        # Could also use pyproj or something or even reprojecting within Visum itself

        print payload.netobj, payload.ids,
        for i, (fname, gtype) in enumerate(payload.ids):
            # Begin transaction, temp table, oh god the train is approaching my stop
            # "ST_GeomFromEWKT('{wkt}')".format(**{"wkt": ewkt})

    @classmethod
    def log(self, message):
        print "Database:", message

class Utility:
    def __init__(self):
        pass
    @staticmethod
    def guessDType(field):
        pass
    @staticmethod
    def _strFieldDtypes(field_dtypes):
        return ", ".join(map(lambda fd:" ".join(["{{{0}}}".format(i) for i in xrange(len(fd))]).format(*fd), field_dtypes))
    @classmethod
    def _strFields(self, field_dtypes):
        return "({0})".format(self._strFieldDtypes(map(lambda v:(v,), zip(*field_dtypes)[0]))) if field_dtypes is not None else ""
    @classmethod
    def formatCreate(self, tblname, field_dtypes, soft_touch = True):
        qry = "CREATE TABLE {ifne} {tname} ({fdefs});"
        return qry.format(**{
            "ifne": "IF NOT EXISTS " if soft_touch else "",
            "tname": tblname,
            "fdefs": self._strFieldDtypes(field_dtypes)
        })
    @classmethod
    def formatInsert(self, con, tblname, values, field_dtypes = None):
        # cur.mogrify requires a valid psycopg2.extensions.connection
        # (it does stuff like read the encoding from the connection)
        cur = con.cursor()
        qry = "INSERT INTO {tname} {fdefs} VALUES ({vals})"
        return qry.format(**{
            "tname": tblname,
            "fdefs": self._strFields(field_dtypes),
            "vals": cur.mogrify(",".join("%s" for _ in values), values)
        })