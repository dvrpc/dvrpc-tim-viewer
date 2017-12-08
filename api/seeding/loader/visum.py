import pythoncom
import sys
import threading
import win32com.client

import numpy

import database

import time

MODEL_SRID = 26918

# TOD DEPENDENT
NETOBJ_ATTRIBUTES = {
    "Links": [("V0PrT","DOUBLE PRECISION")]
}

# TOD DEPENDENT
MTXs = [
    210, # IMP
    220, # IVT
    250, # OVT
    260, # TOL
    270, # DIS
    290, # TTC
    291, # UDS
    400, # IPD
    420, # IVT
    421, # IVTT(RR)
    422, # IVTT(Sub)
    423, # IVTT(Pat)
    424, # IVTT(LRT)
    426, # IVTT(BRT)
    428, # IVTT(Bus)
    429, # IVTT(Trl)
    450, # OVT
    451, # OWTA
    460, # FAR
    480, # NTR
    481, # XIMP
    490, # JRT
]

MTX_UPPERLIMIT = 1e5

# Generated automanually using Utility.GetUsableAttributes below
# and manually finding/translating identifying fields
# TOD INDEPENDENT
# Note: Commented out sections threw a Visum COM Error that ultimately relates
# to licensing. Short story long, it was not used, I'm ignoring them.
NETOBJ_IDs = {
    # u'BlockItemTypes': [(u'NO', 'INTEGER')],
    # u'BlockItems': [(u'BLOCKID', 'INTEGER'),
                    # (u'BLOCKINGDAY', 'INTEGER'),
                    # (u'STARTDAYINDEX', 'INTEGER'),
                    # (u'STARTTIME', 'TEXT'),
                    # (u'VEHJOURNEYNO', 'INTEGER'),
                    # (u'VEHJOURNEYSECTIONNO', 'INTEGER')],
    # u'BlockVersions': [(u'ID', 'INTEGER')],
    # u'Blocks': [(u'ID', 'INTEGER')],
    u'Connectors': [(u'ZONENO', 'INTEGER'),
                    (u'NODENO', 'INTEGER'),
                    (u'DIRECTION', 'TEXT')],
    u'CountLocations': [(u'NO', 'INTEGER')],
    u'Crosswalks': [(u'NODENO', 'INTEGER'),
                    (u'MAINNODENO', 'INTEGER'),
                    (u'ORIENTATION', 'TEXT'),
                    (u'INDEX', 'INTEGER'),
                    (u'DIRECTION', 'INTEGER')],
    u'DemandSegments': [(u'CODE', 'TEXT')],
    u'Detectors': [(u'NO', 'INTEGER')],
    u'Directions': [(u'NO', 'INTEGER')],
    u'GeometryTemplates': [(u'NO', 'INTEGER')],
    u'LegTemplates': [(u'NO', 'INTEGER')],
    u'LineRouteItems': [(u'LINENAME', 'TEXT'),
                        (u'LINEROUTENAME', 'TEXT'),
                        (u'DIRECTIONCODE', 'TEXT'),
                        (u'INDEX', 'INTEGER')],
    u'LineRoutes': [(u'LINENAME', 'TEXT'),
                    (u'NAME', 'TEXT'),
                    (u'DIRECTIONCODE', 'TEXT')],
    u'Lines': [(u'NAME', 'TEXT')],
    u'LinkTypes': [(u'NO', 'INTEGER')],
    u'Links': [(u'NO', 'INTEGER'),
               (u'FROMNODENO', 'INTEGER'),
               (u'TONODENO', 'INTEGER')],
    u'MainLines': [(u'NAME', 'TEXT')],
    u'MainNodes': [(u'NO', 'INTEGER')],
    u'MainTurns': [(u'FROMNODENO', 'INTEGER'),
                   (u'FROMCORDONNODENO', 'INTEGER'),
                   (u'TOCORDONNODENO', 'INTEGER'),
                   (u'TONODENO', 'INTEGER')],
    u'MainZones': [(u'NO', 'INTEGER')],
    u'Modes': [(u'CODE', 'TEXT')],
    u'Nodes': [(u'NO', 'INTEGER')],
    u'Operators': [(u'NO', 'INTEGER')],
    u'PathSets': [(u'NO', 'INTEGER')],
    u'Paths': [(u'SETNO', 'INTEGER'), (u'NO', 'INTEGER')],
    # u'PropagationLinkInfos': [(u'FROMNODENO', 'INTEGER'),
                              # (u'TONODENO', 'INTEGER'),
                              # (u'DESTZONENO', 'INTEGER')],
    u'Screenlines': [(u'NO', 'INTEGER')],
    u'SignalControls': [(u'NO', 'INTEGER')],
    u'SignalGroups': [(u'SCNO', 'INTEGER'), (u'NO', 'INTEGER')],
    u'Stages': [(u'SCNO', 'INTEGER'), (u'NO', 'INTEGER')],
    u'StopAreas': [(u'NO', 'INTEGER')],
    u'StopPoints': [(u'NO', 'INTEGER')],
    u'Stops': [(u'NO', 'INTEGER')],
    u'TSystems': [(u'CODE', 'TEXT')],
    u'Territories': [(u'NO', 'INTEGER')],
    u'TicketTypes': [(u'NO', 'INTEGER')],
    u'TimeProfileItems': [(u'LINENAME', 'TEXT'),
                          (u'LINEROUTENAME', 'TEXT'),
                          (u'DIRECTIONCODE', 'TEXT'),
                          (u'TIMEPROFILENAME', 'TEXT'),
                          (u'INDEX', 'INTEGER')],
    u'TimeProfiles': [(u'LINENAME', 'TEXT'),
                      (u'LINEROUTENAME', 'TEXT'),
                      (u'DIRECTIONCODE', 'TEXT'),
                      (u'NAME', 'TEXT')],
    u'TollSystems': [(u'NO', 'INTEGER')],
    u'Turns': [(u'FROMNODENO', 'INTEGER'),
               (u'VIANODENO', 'INTEGER'),
               (u'TONODENO', 'INTEGER')],
    u'ValidDaysCont': [(u'NO', 'INTEGER')],
    u'VehJourneySections': [(u'VEHJOURNEYNO', 'INTEGER'), (u'NO', 'INTEGER')],
    u'VehicleCombinations': [(u'NO', 'INTEGER')],
    u'VehicleJourneyItems': [(u'VEHJOURNEYNO', 'INTEGER'), (u'INDEX', 'INTEGER')],
    u'VehicleJourneys': [(u'NO', 'INTEGER')],
    u'VehicleUnits': [(u'NO', 'INTEGER')],
    u'Zones': [(u'NO', 'INTEGER')]
}

# I knew I wanted a thread manager
class VisumManager(threading.Thread):
    TODs = ["AM","MD","PM","NT"]
    def __init__(self, path_template, vernum, queue):
        super(VisumManager, self).__init__()
        self.path_template = path_template
        self.vernum = vernum
        self.queue = queue
        self._threads = []
    def run(self):
        for TOD in self.TODs:
            v = VisumDataMiner(self.path_template.format(**{"tod":TOD}), self.vernum, self.queue)
            v.start()
            self._threads.append(v)
        for t in self._threads:
            t.join()

class VisumDataMiner(threading.Thread):
    def __init__(self, path, vernum, queue):
        super(VisumDataMiner, self).__init__()
        self.path = path
        self.vernum = vernum
        self.queue = queue
        self._index_templates = {}
        self.tod = None

    def run(self):
        sys.coinit_flags = 0
        pythoncom.CoInitialize()
        v = self.CreateVisum()
        self.tod = v.Net.AttValue("TOD")

        self.GetNetObjects(v)
        self.GetAttributes(v)
        self.GetMatrices(v)
        self.GetGeometries(v)
        pythoncom.CoUninitialize()

    def CreateVisum(self):
        v = win32com.client.Dispatch("Visum.Visum-64.{vn}".format(**{"vn":self.vernum}))
        v.LoadVersion(self.path)
        return v

    def GetNetObjects(self, Visum):
        for netobj, ids in self.iterNetObjGroupIDs():
            print netobj
            payload = zip(*map(lambda (id, dtype):self.GetVisumAttribute(Visum, netobj, id), ids))
            if len(payload) > 0:
                self.queue.put(Sponge(**{
                    "type": database.TBL_NETOBJ,
                    "netobj": netobj,
                    "atts": ids,
                    "data": payload
                }))
    def GetAttributes(self, Visum):
        for netobj, ids in self.iterNetObjGroupAttributes():
            payload = zip(*map(lambda (id, dtype):self.GetVisumAttribute(Visum, netobj, id), ids))
            if len(payload) > 0:
                self.queue.put(Sponge(**{
                    "type": database.TBL_DATA,
                    "tod": self.tod,
                    "netobj": netobj,
                    "atts": ids,
                    "data": payload
                }))
    def GetMatrices(self, Visum):
        for mtxno in self.iterMatrices():
            mtx_listing = self._getMatrix(Visum, mtxno)
            self.queue.put(Sponge(**{
                "type": database.TBL_MATRIX,
                "tod": self.tod,
                "mtxno": mtxno,
                "data": mtx_listing
            }))
    def _getMatrix(self, Visum, mtxno):
        mtx = self.GetVisumMatrix(Visum, mtxno)
        if not mtx.shape in self._index_templates:
            n,n = mtx.shape
            y = numpy.vstack((numpy.arange(n) for _ in xrange(n)))
            x = y.T.flatten()
            y = y.flatten()
            self._index_templates[mtx.shape] = (x, y)
        else:
            x, y = self._index_templates[mtx.shape]
        z = mtx.flatten()
        mtx_listing = numpy.array((x,y,z,), dtype = object).T
        return mtx_listing[numpy.where(mtx_listing[:,2] < MTX_UPPERLIMIT)]
    def GetGeometries(self, Visum):
        # Need to include the related network object identifiers
        for netobj, geomfields in self.iterNetObjectGroup(self._getGeometryFields(Visum)):
            if not netobj in NETOBJ_IDs:
                print "Warning, {0} not included in NETOBJ_IDs".format(netobj)

            ids = []
            payload = []
            for gfield in geomfields:
                data = self.GetVisumAttribute(Visum, netobj, gfield)
                if len(data) > 0:
                    gdtype = set(zip(*map(lambda v:v.split("(",1), data))[0])
                    # Could warn if len(gdtype) <> 1, I don't think PostGIS likes mix geometry type fields
                    ids.append((gfield, gdtype))
                    payload.append(map(
                        lambda v:"SRID={srid};".format(**{"srid":MODEL_SRID}) + v,
                        data
                    ))

            if len(payload) > 0:
                self.queue.put(Sponge(**{
                    "type": database.TBL_GEOMETRY,
                    "netobj": netobj,
                    "ids": ids,
                    "data": payload
                }))
    def _getGeometryFields(self, Visum):
        netobj_geometry = {}
        attributes = Utility.GetCOMAttributes(Visum)
        wkt_fields = filter(lambda row:"wkt" in row[1].lower(), attributes)
        for netobj in set(zip(*wkt_fields)[0]):
            netobj_geometry[netobj] = zip(*filter(lambda row:row[0] == netobj, wkt_fields))[1]
        return netobj_geometry

    @staticmethod
    def GetVisumAttribute(Visum, netobj, att):
        return map(lambda (i,v):v, getattr(Visum.Net, netobj).GetMultiAttValues(att))
    @staticmethod
    def GetVisumMatrix(Visum, mtxno):
        return numpy.array(Visum.Net.Matrices.ItemByKey(mtxno).GetValues())
    @staticmethod
    def iterNetObjIDs():
        for netobj, ids in NETOBJ_IDs.iteritems():
            for id, dtype in ids:
                yield netobj, id
    @staticmethod
    def iterNetObjectGroup(dictionary):
        for netobj, ids in dictionary.iteritems():
            yield netobj, ids
    @classmethod
    def iterNetObjGroupIDs(self):
        return self.iterNetObjectGroup(NETOBJ_IDs)
    @classmethod
    def iterNetObjGroupAttributes(self):
        return self.iterNetObjectGroup(NETOBJ_ATTRIBUTES)
    @staticmethod
    def iterMatrices():
        for mtxno in MTXs:
            yield mtxno

class Sponge:
    def __init__(self, **kwds):
        for k, v in kwds.iteritems():
            setattr(self, k, v)
    def __contains__(self, key):
        return hasattr(self, key)

class Utility:
    tempfile = __import__("tempfile")
    os = __import__("os")
    # Due to various inconsistencies, manual review is required
    ATTRIBUTE_PATCH = {
        u"poicategory": u"POICategories",
        u"territory": u"Territories",
        u"tsys": u"TSystems",
        u"validdays": u"ValidDaysCont", # (?)
        u"vehcomb": u"VehicleCombinations",
        u"vehjourney": u"VehicleJourneys",
        u"vehjourneyitem": u"VehicleJourneyItems",
        u"vehunit": u"VehicleUnits",
    }
    def __init__(self):
        pass
    @staticmethod
    def enumerateCOM(object, bruteForceN = 1000):
        methods, attributes = [], []
        for i in xrange(bruteForceN):
            try:
                sig = object._lazydata_[0].GetNames(i)
            except:
                pass
            else:
                if (len(sig) > 1):
                    methods.append(sig)
                else:
                    attributes.append(sig)
        return (methods, attributes)
    @staticmethod
    def GetFullAccessDB(Visum, path_accdb):
        Visum.SaveAccessDatabase(
            DatabasePath = path_accdb,
            LayoutFile = "",
            editableOnly = False, # Default: True
            nonDefaultOnly = True, # Default: False
            activeNetElemsOnly = False,
            nonEmptyTablesOnly = False
        )
    @classmethod
    def GetCOMAttributes(self, Visum):
        master_attributes = []
        methods, attributes = self.enumerateCOM(Visum.Net)
        for (att,) in sorted(attributes):
            COMobj = getattr(Visum.Net, att)
            _methods, _attributes = self.enumerateCOM(COMobj)
            if ("Attributes",) in _attributes:
                for COMatt in COMobj.Attributes.GetAll:
                    master_attributes.append((att, COMatt.Code))
        return master_attributes
    @classmethod
    def GetUsableAttributes(self, Visum):
        filehandle, path_temp = self.tempfile.mkstemp()
        # Thanks for all the extra bullshit tempfile
        os.close(filehandle)
        os.remove(path_temp)
        self.GetFullAccessDB(Visum, path_temp)
        accdb = Access(path_temp)
        COM_atts = self.GetCOMAttributes(Visum)
        COM_netobj = dict((netobj.lower(), netobj) for netobj in set(zip(*COM_atts)[0]))

        netobj_ids = {}
        for netobj, field, dtype in accdb.iterAllTableFields(notNullable = 1):
            netobj = netobj.lower()
            _netobj = None
            if netobj in COM_netobj:
                _netobj = COM_netobj[netobj]
            elif (netobj + 's') in COM_netobj:
                _netobj = COM_netobj[netobj + 's']
            elif netobj in self.ATTRIBUTE_PATCH:
                _netobj = self.ATTRIBUTE_PATCH[netobj]
            else:
                continue
            if not _netobj in netobj_ids:
                netobj_ids[_netobj] = []
            netobj_ids[_netobj].append((field, accdb.ACCESS_POSTGRES_DTYPES[dtype]))

        accdb.close()
        os.remove(path_temp)
        return netobj_ids

class Access:
    pypyodbc = __import__("pypyodbc")
    sqlite3 = __import__("sqlite3")
    ACCESS_SYS_TABLES = [
        "msysaccessstorage",
        "msysaccessxml",
        "msysnavpanegroupcategories",
        "msysnavpanegroups",
        "msysnavpanegrouptoobjects",
        "msysresources"
    ]
    SQL_CREATE_TBL_FIELDS = """
    CREATE TABLE fields (
        table_cat text,
        table_schem text,
        table_name text not null,
        column_name text not null,
        data_type integer not null,
        type_name text not null,
        column_size integer,
        buffer_length integer,
        decimal_digits integer,
        num_prec_radix integer,
        nullable integer,
        remarks text,
        column_def text,
        sql_data_type integer not null,
        sql_datetime_sub integer,
        char_octet_length integer,
        ordinal_position integer not null,
        is_nullable text,
        ordinal_position_redux integer
    );
    """
    SQL_CREATE_TBL_BLACKLIST = """
    CREATE TABLE blacklist (
        table_name text not null
    );
    """
    SQL_INSERT_TBL_FIELDS = """
    INSERT INTO fields VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """
    SQL_INSERT_TBL_BLACKLIST = """
    INSERT INTO blacklist VALUES (?);
    """
    SQL_SELECT_TBL_FIELDS_TABLENAMES = """
    SELECT DISTINCT(table_name) table_name
    FROM fields
    WHERE LOWER(table_name) NOT IN (SELECT * FROM blacklist)
    ORDER BY table_name;
    """
    SQL_SELECT_TBL_FIELDS_COLUMNSxTABLENAMES = """
    SELECT table_name, column_name, type_name
    FROM fields WHERE table_name = ? AND nullable <> ?;
    """
    ACCESS_SQLITE_DTYPES = {
        "COUNTER": "INTEGER", # Unsure
        "DATETIME": "TEXT", # Unsure
        "DOUBLE": "REAL",
        "INTEGER": "INTEGER",
        "LONGBINARY": "BLOB",
        "LONGCHAR": "TEXT",
        "VARCHAR": "TEXT"
    }
    ACCESS_POSTGRES_DTYPES = {
        "COUNTER": "INTEGER", # Unsure
        "DATETIME": "TEXT", # Unsure
        "DOUBLE": "DOUBLE PRECISION",
        "INTEGER": "INTEGER",
        "LONGBINARY": "BLOB",
        "LONGCHAR": "TEXT",
        "VARCHAR": "TEXT"
    }
    ACCESS_PYTHON_DTYPES = {
        "COUNTER": int, # Unsure
        "DATETIME": str, # Unsure
        "DOUBLE": float,
        "INTEGER": int,
        "LONGBINARY": lambda v:v, # NOOP
        "LONGCHAR": str,
        "VARCHAR": str
    }

    def __init__(self, path_accdb, path_sqlite = ":memory:"):
        self.path_accdb = path_accdb
        self.path_sqlite = path_sqlite
        self.con_accdb = self.pypyodbc.win_connect_mdb(path_accdb)
        self.con_sqlite = self.sqlite3.connect(path_sqlite)
        self._createSQLiteDB()
    def _createSQLiteDB(self):
        cur = self.con_sqlite.cursor()
        cur.execute(self.SQL_CREATE_TBL_FIELDS)
        cur.executemany(self.SQL_INSERT_TBL_FIELDS, list(self.con_accdb.cursor().columns()))
        cur.execute(self.SQL_CREATE_TBL_BLACKLIST)
        cur.executemany(self.SQL_INSERT_TBL_BLACKLIST, map(lambda v:(v,), self.ACCESS_SYS_TABLES))
        self.con_sqlite.commit()
    def close(self):
        self.con_accdb.close()
        self.con_sqlite.close()
    def iterTables(self):
        cur = self.con_sqlite.cursor()
        cur.execute(self.SQL_SELECT_TBL_FIELDS_TABLENAMES)
        for (tblname,) in cur.fetchall():
            yield tblname
    def iterTableFields(self, tblname, notNullable = -1, leadTableName = True):
        """
            notNullable:
               -1: All
                0: False - Data fields?
                1: True - Key fields?
        """
        cur = self.con_sqlite.cursor()
        cur.execute(self.SQL_SELECT_TBL_FIELDS_COLUMNSxTABLENAMES, (tblname, notNullable))
        payload = cur.fetchall()
        for row in (payload if leadTableName else map(lambda t,c,d:(c,d), payload)):
            yield row
    def iterAllTableFields(self, notNullable = -1):
        for tblname in self.iterTables():
            for row in self.iterTableFields(tblname, notNullable):
                yield row