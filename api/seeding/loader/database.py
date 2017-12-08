# Note:
# All data processing should take place in Visum.py
# Only database-specific processing should be here
# e.g. PostGIS overhead

import csv
import logging
logger = logging.getLogger(__name__)
import StringIO
import threading

import psycopg2 as psql

from common import *

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
    def __init__(self, db_credentials, queue, max_queue_depth):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
        self.queue = queue
        self.con = psql.connect(**self.db_credentials)
        self.max_queue_depth = max_queue_depth
        logger.debug("Database.__init__(): Done")

    def run(self):
        while True:
            payload = self.queue.get()
            if payload is None:
                self.con.commit()
                self.con.close()
                break
            if "type" in payload:
                self.process(payload)
            else:
                logger.error("Database.run(): Missing payload type")

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
            logger.error("Database.process(): Invalid table type (%s)", payload.type)

    def LoadAttributes(self, payload, noTOD = False):
        if noTOD:
            tblname = TBL_NAMETMPLT_NETOBJ.format(**{'netobj':payload.netobj})
        else:
            tblname = TBL_NAMETMPLT_DATA.format(**{'netobj':payload.netobj,'tod':payload.tod})
        logger.debug("Database.LoadAttributes(): Importing %s", tblname)
        cur = self.con.cursor()
        cur.execute(Utility.formatCreate(tblname, payload.atts))
        for row in payload.data:
            cur.execute(Utility.formatInsert(self.con, tblname, row, payload.atts))
        self.con.commit()
    def LoadMatrix(self, payload):
        tblname = TBL_NAMETMPLT_MTX.format(**{'mtxno': payload.mtxno, 'tod': payload.tod})
        logger.debug("Database.LoadMatrix(): Importing %s", tblname)
        f = self._bufferMatrix(payload.data)
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
    def LoadGeometries(self, payload):
        assert len(payload.data) == len(payload.gdata), "Warning: Count mismatch"
        tblname = TBL_NAMETMPLT_GEOMETRY.format(**{'netobj':payload.netobj})
        logger.debug("Database.LoadGeometries(): Importing %s", tblname)
        atts = payload.atts + map(lambda r:(lambda f,d,*a:(f,"geometry({0},{1})".format(d,payload.srid)) + a)(*r), payload.gatts)
        cur = self.con.cursor()
        cur.execute(Utility.formatCreate(tblname, atts))
        for i in xrange(len(payload.data)):
            cur.execute(Utility.formatGeometryInsert(self.con, tblname, payload.data[i], payload.gdata[i], atts))
        self.con.commit()
    def _bufferMatrix(self, mtx_listing):
        f = StringIO.StringIO()
        w = csv.writer(f)
        w.writerows(mtx_listing)
        f.seek(0)
        return f

    def getProjectionWKT(self, srid):
        cur = self.con.cursor()
        cur.execute("SELECT srtext FROM spatial_ref_sys WHERE srid = %s", (srid,))
        (prjwkt,) = cur.fetchone()
        return prjwkt
    def nukeDatabase(self):
        cur = self.con.cursor()
        cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' and tablename <> 'spatial_ref_sys';")
        for table, in cur.fetchall():
            cur.execute("DROP TABLE {0}".format(table))
        self.con.commit()

class Utility:
    def __init__(self):
        pass
    @staticmethod
    def guessDType(field):
        pass
    @staticmethod
    def _strFieldDtypes(field_dtypes):
        return ", ".join(map(
            lambda fd:" ".join(["{{{0}}}".format(i) for i in xrange(len(fd))]).format(*fd),
            field_dtypes
        ))
    @classmethod
    def _strFields(self, field_dtypes):
        return "({0})".format(self._strFieldDtypes(map(lambda v:(v,), zip(*field_dtypes)[0]))) if field_dtypes is not None else ""
    @classmethod
    def _strGeos(self, cur, values, postgisfn):
        return "," + cur.mogrify(",".join(postgisfn for _ in values), values) if values else ""
    @classmethod
    def formatCreate(self, tblname, field_dtypes, soft_touch = True):
        qry = "CREATE TABLE {ifne} {tname} ({fdefs});"
        return qry.format(**{
            "ifne": "IF NOT EXISTS " if soft_touch else "",
            "tname": tblname,
            "fdefs": self._strFieldDtypes(field_dtypes)
        })
    @classmethod
    def _formatInsert(self, con, tblname, values, geoms = None, field_dtypes = None, postgisfn = None):
        # cur.mogrify requires a valid psycopg2.extensions.connection
        # (it does stuff like read the encoding from the connection)
        cur = con.cursor()
        return "INSERT INTO {tname} {fdefs} VALUES ({vals}{geos})".format(**{
            "tname": tblname,
            "fdefs": self._strFields(field_dtypes),
            "vals": cur.mogrify(",".join("%s" for _ in values), values),
            "geos": self._strGeos(cur, geoms, postgisfn),
        })
    @classmethod
    def formatInsert(self, con, tblname, values, field_dtypes = None):
        return self._formatInsert(con, tblname, values, field_dtypes = field_dtypes)
    @classmethod
    def formatGeometryInsert(self, *args, **kwds):
        return self._formatInsert(*args, postgisfn = "ST_GeomFromEWKT(%s)", **kwds)