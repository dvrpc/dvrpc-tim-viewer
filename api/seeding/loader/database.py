# Note:
# All data processing should take place in Visum.py
# Only database-specific processing should be here
# e.g. PostGIS overhead

import csv
import logging
logger = logging.getLogger(__name__)
import queue
import io
import threading

import psycopg2 as psql

from loader.common import *

import time

INSERT_BATCH_SIZE = 10000

# TOD agnostic
TBL_NETOBJ = "net"
# TOD dependent
TBL_DATA = "dat"
# TOD dependent
TBL_MATRIX = "mtx"
# TOD agnostic(?)
TBL_GEOMETRY = "geom"

TBL_NAMETMPLT_NETOBJ = "net_{netobj}"
TBL_NAMETMPLT_MTX = "mtx_{mtxno}"
TBL_NAMETMPLT_DATA = "dat_{netobj}"
TBL_NAMETMPLT_GEOMETRY = "geom_{netobj}"

# "CREATE TABLE {tblname} ({fields})"
# "ALTER TABLE {tblname} ADD COLUMN ({fname} {dtype})"
# "INSERT INTO {tblname} VALUES ({nargs})"

SQL_CREATE_TBL_MTX = "CREATE TABLE IF NOT EXISTS {0} (oindex smallint, dindex smallint, scen text, tod text, val double precision);"
SQL_CREATE_IDX_MTX_O = "CREATE INDEX IF NOT EXISTS {0}_o_idx ON public.{0} (oindex ASC NULLS LAST);"
SQL_CREATE_IDX_MTX_D = "CREATE INDEX IF NOT EXISTS {0}_d_idx ON public.{0} (dindex ASC NULLS LAST);"
SQL_CREATE_IDX_GEOM = "CREATE INDEX {tblname}_{field}_gidx ON {tblname} USING GIST ({field});"

class DatabaseManager(threading.Thread):
    def __init__(self, db_credentials, dataqueue, max_queue_depth, num_threads, overwrite_existing_tables):
        super(DatabaseManager, self).__init__()
        self.db_credentials = db_credentials
        self.dataqueue = dataqueue
        self.max_queue_depth = max_queue_depth
        self.num_threads = num_threads
        self.overwrite_existing_tables = overwrite_existing_tables
        self._queue = queue.Queue()
        self._threads = []
        self._initialiseWorkers()
        self._con = psql.connect(**db_credentials)
        logger.debug("DatabaseManager.__init__(): Done")
    def run(self):
        while True:
            payload = self.dataqueue.get()
            if payload is None:
                for _ in self._threads:
                    self._queue.put(None)
                break
            else:
                self._queue.put(payload)
        for t in self._threads:
            t.join()
        logger.debug("DatabaseManager.run(): Done")
    def _initialiseWorkers(self):
        for i in range(self.num_threads):
            self._threads.append(Database(
                self.db_credentials,
                self._queue,
                self.max_queue_depth,
                self.overwrite_existing_tables
            ))
        for t in self._threads:
            t.start()
        return
    def getProjectionWKT(self, srid):
        cur = self._con.cursor()
        cur.execute("SELECT srtext FROM spatial_ref_sys WHERE srid = %s", (srid,))
        (prjwkt,) = cur.fetchone()
        return prjwkt
    def nukeDatabase(self):
        cur = self._con.cursor()
        cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' and tablename <> 'spatial_ref_sys';")
        for table, in cur.fetchall():
            cur.execute("DROP TABLE {0}".format(table))
        self._con.commit()

class Database(threading.Thread):
    MTX_DEFAULT_COLUMNS = ["oindex", "dindex", "val"]
    def __init__(self, db_credentials, dataqueue, max_queue_depth, overwrite_existing_tables):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
        self.dataqueue = dataqueue
        self.con = psql.connect(**self.db_credentials)
        self.max_queue_depth = max_queue_depth
        self.overwrite_existing_tables = overwrite_existing_tables
        logger.debug("Database.__init__(): Done")

    def run(self):
        while True:
            logger.debug("Database-%d.run(): Waiting...", self.ident)
            payload = self.dataqueue.get()
            if payload is None:
                self.con.commit()
                self.con.close()
                break
            if "type" in payload:
                self.process(payload)
            else:
                logger.error("Database.run(): Missing payload type")
        logger.debug("Database-%d.run(): Done", self.ident)

    def process(self, payload):
        # Oh switch statement, where art thou?
        if   payload.type == TBL_NETOBJ:
            self.LoadAttributes(payload)
        elif payload.type == TBL_DATA:
            self.LoadTODAttributes(payload)
        elif payload.type == TBL_MATRIX:
            self.LoadMatrix(payload)
        elif payload.type == TBL_GEOMETRY:
            self.LoadGeometries(payload)
        else:
            logger.error("Database.process(): Invalid table type (%s)", payload.type)
    def LoadAttributes(self, payload):
        tblname = TBL_NAMETMPLT_NETOBJ.format(**{'netobj':payload.netobj})
        if self.skipTable(tblname):
            logger.debug("Database-%d.LoadAttributes(): Exists, skipped %s", self.ident, tblname)
            return
        logger.debug("Database-%d.LoadAttributes(): Importing %s", self.ident, tblname)
        cur = self.con.cursor()
        atts = payload.atts + [[u"scen", u"TEXT"]]
        try:
            cur.execute(Utility.formatCreate(tblname, atts))
        except:
            logger.debug("Database-%d.LoadAttributes(): Table already does exist %s", self.ident, tblname)
        else:
            self.con.commit()
        finally:
            cur = self.con.cursor()
        for data in self._iterPayload(payload.data):
            cur.execute(
                Utility.formatMultiInsert(
                    self.con,
                    tblname,
                    list(map(lambda a:a + (payload.scen,), data)),
                    atts
                )
            )
        self.con.commit()
    def LoadTODAttributes(self, payload):
        tblname = TBL_NAMETMPLT_DATA.format(**{'netobj':payload.netobj})
        if self.skipTable(tblname):
            logger.debug("Database-%d.LoadAttributes(): Exists, skipped %s", self.ident, tblname)
            return
        logger.debug("Database-%d.LoadAttributes(): Importing %s", self.ident, tblname)
        cur = self.con.cursor()
        atts = payload.atts + [[u"scen", u"TEXT"], [u"tod", u"TEXT"]]
        qry = Utility.formatCreate(tblname, atts)
        # logging.debug("Database-%d:LoadAttributes(): Create statement: %s", self.ident, qry)
        try:
            cur.execute(qry)
        except:
            logging.debug("Database-%d.LoadTODAttributes(): Table already does exist %s", self.ident, tblname)
        else:
            self.con.commit()
        finally:
            cur = self.con.cursor()
        for data in self._iterPayload(payload.data):
            cur.execute(
                Utility.formatMultiInsert(
                    self.con,
                    tblname,
                    list(map(lambda a:a + (payload.scen, payload.tod,), data)),
                    atts
                )
            )
        self.con.commit()
    def LoadMatrix(self, payload):
        tblname = TBL_NAMETMPLT_MTX.format(**{'mtxno': payload.mtxno})
        if self.skipTable(tblname):
            logger.debug("Database-%d.LoadMatrix(): Exists, skipped %s", self.ident, tblname)
            return
        logger.debug("Database-%d.LoadMatrix(): Importing %s", self.ident, tblname)
        f = self._bufferMatrix(payload.data, addtl_fields = [payload.scen, payload.tod])
        cur = self.con.cursor()
        try:
            cur.execute(SQL_CREATE_TBL_MTX.format(tblname))
        except:
            logger.debug("Database-%d.LoadMatrix(): Table already does exist %s", self.ident, tblname)
        else:
            self.con.commit()
        finally:
            cur = self.con.cursor()
        cur.copy_from(
            f,
            tblname,
            columns = self.MTX_DEFAULT_COLUMNS + ["scen", "tod"],
            sep = ','
        )
        f.close()
        # cur.execute(SQL_CREATE_IDX_MTX_O.format(tblname))
        # cur.execute(SQL_CREATE_IDX_MTX_D.format(tblname))
        self.con.commit()
    def LoadGeometries(self, payload):
        assert len(payload.data) == len(payload.gdata), "Error: Count mismatch"
        tblname = TBL_NAMETMPLT_GEOMETRY.format(**{'netobj':payload.netobj})
        if self.skipTable(tblname):
            logger.debug("Database-%d.LoadGeometries(): Exists, skipped %s", self.ident, tblname)
            return
        logger.debug("Database-%d.LoadGeometries(): Importing %s", self.ident, tblname)
        atts = payload.atts + list(map(lambda r:(lambda retval:(retval[0],"geometry({0},{1})".format(retval[1],payload.srid)) + retval[2:])(*r), payload.gatts))
        cur = self.con.cursor()
        try:
            cur.execute(Utility.formatCreate(tblname, atts))
        except:
            logger.debug("Database-%d.LoadGeometries(): Table already does exist %s", self.ident, tblname)
        else:
            self.con.commit()
        finally:
            cur = self.con.cursor()
        for _data in self._iterPayload(list(zip(payload.data, payload.gdata))):
            data, gdata = list(zip(*_data))
            cur.execute(Utility.formatMultiGeometryInsert(self.con, tblname, data, gdata, atts))
        for field, dtype in payload.gatts:
            cur.execute(SQL_CREATE_IDX_GEOM.format(**{"tblname": tblname, "field": field}))
        self.con.commit()
    def _bufferMatrix(self, mtx_listing, addtl_fields = []):
        f = io.StringIO()
        w = csv.writer(f)
        for row in mtx_listing:
            w.writerow(row.tolist() + addtl_fields)
        # w.writerows(mtx_listing)
        f.seek(0)
        return f
    def _iterPayload(self, data):
        for i in range(0, len(data), INSERT_BATCH_SIZE):
            yield data[i:i+INSERT_BATCH_SIZE]
    def skipTable(self, tblname):
        return self.overwrite_existing_tables if Utility.doesTableExist(self.con, tblname) else False


class Utility:
    def __init__(self):
        pass
    @staticmethod
    def guessDType(field):
        pass
    @staticmethod
    def _strFieldDtypes(field_dtypes):
        return ", ".join(list(map(
            lambda fd:" ".join(["{{{0}}}".format(i) for i in range(len(fd))]).format(*fd),
            field_dtypes
        )))
    @classmethod
    def _strFields(self, field_dtypes):
        return "({0})".format(self._strFieldDtypes(
            list(map(lambda v:(v,), list(zip(*field_dtypes))[0]))
        )) if field_dtypes is not None else ""
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
    @staticmethod
    def _iterRecordGeoms(records, geom_records = None):
        _geom = True if geom_records else False
        for i, values in enumerate(records):
            if _geom:
                yield (values, geom_records[i])
            else:
                yield (values, None)
    @classmethod
    def _formatInsert(self, con, tblname, records, geom_records = None, field_dtypes = None, postgisfn = None):
        # cur.mogrify requires a valid psycopg2.extensions.connection
        # (it does stuff like read the encoding from the connection)
        cur = con.cursor()
        values = ",".join([
            "({0}{1})".format(
                cur.mogrify(",".join("%s" for _ in r), r),
                self._strGeos(cur, g, postgisfn)
            ) for r, g in self._iterRecordGeoms(records, geom_records)
        ])
        return "INSERT INTO {tname} {fdefs} VALUES {values}".format(**{
            "tname": tblname,
            "fdefs": self._strFields(field_dtypes),
            "values": values
        })
    @classmethod
    def formatInsert(self, con, tblname, values, field_dtypes = None):
        return self._formatInsert(con, tblname, (values,), field_dtypes = field_dtypes)
    @classmethod
    def formatMultiInsert(self, con, tblname, records, field_dtypes = None):
        return self._formatInsert(con, tblname, records, field_dtypes = field_dtypes)
    @classmethod
    def formatGeometryInsert(self, con, tblname, values, geoms, field_dtypes):
        return self._formatInsert(con, tblname, (values,), (geoms,), field_dtypes, postgisfn = "ST_GeomFromEWKT(%s)")
    @classmethod
    def formatMultiGeometryInsert(self, *args, **kwds):
        return self._formatInsert(*args, postgisfn = "ST_GeomFromEWKT(%s)", **kwds)
    @staticmethod
    def doesTableExist(con, tblname):
        cur = con.cursor()
        # Added in Postgres 9.4, returns None if not found
        cur.execute("SELECT to_regclass(%s)", (tblname,))
        (found,) = cur.fetchone()
        return True if found else False