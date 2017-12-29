import logging
logger = logging.getLogger(__name__)
import pythoncom
import re
import sys
import threading
import win32com.client

import numpy

import database
from common import *

import time

# TOD INDEPENDENT
NETOBJ_ATTRIBUTES = {
    "Links": [("V0PrT", "v0prt", "DOUBLE PRECISION")]
}

# TOD DEPENDENT
NETOBJ_TOD_ATTRIBUTES = {
    "Connectors": [
        ("VolVehPrT(AP)"                                "vol_auto",                 "DOUBLE PRECISION"),
        ("VolPersPuT(AP)"                               "vol_transit",              "DOUBLE PRECISION")
    ],
    "Links": [
        ("VOLVEHPRT(AP)",                               "vol_auto",                 "DOUBLE PRECISION"),
        ("VOLPERS_DSEG(TA,AP)",                         "vol_transit_auto",         "DOUBLE PRECISION"),
        ("VOLPERS_DSEG(TW,AP)",                         "vol_transit_walk",         "DOUBLE PRECISION")
    ],
    "Lines": [
        ("PTRIPSUNLINKED_DSEG(TA,AP)",                  "vol_transit_auto",         "DOUBLE PRECISION"),
        ("PTRIPSUNLINKED_DSEG(TW,AP)",                  "vol_transit_walk",         "DOUBLE PRECISION"),
        ("PTripsUnlinked(AP)",                          "person_trips",             "DOUBLE PRECISION"),
        ("PassMiTrav(AP)",                              "pass_miles",               "DOUBLE PRECISION"),
        ("Sum:LineRoutes\Sum:StopPoints\PassBoard(AP)", "line_boardings",           "DOUBLE PRECISION")
    ],
    "StopAreas": [
        ("Sum:StopPoints\PassBoard(AP)",                "sa_boardings",             "DOUBLE PRECISION")
    ],
    "StopPoints": [
        ("PassBoard(AP)",                               "sp_boards",                "DOUBLE PRECISION"),
        ("PassAlight(AP)",                              "sp_alights",               "DOUBLE PRECISION")
    ],
    "Zones": [
        ("OTraffic(Car)"                                "otraffic_car",             "DOUBLE PRECISION"),
        ("OTraffic(TA)"                                 "otraffic_transit_auto",    "DOUBLE PRECISION"),
        ("OTraffic(TW)"                                 "otraffic_transit_walk",    "DOUBLE PRECISION"),
        ("DTraffic(Car)"                                "dtraffic_car",             "DOUBLE PRECISION"),
        ("DTraffic(TA)"                                 "dtraffic_transit_auto",    "DOUBLE PRECISION"),
        ("DTraffic(TW)"                                 "dtraffic_transit_walk",    "DOUBLE PRECISION"),
        ("ITraffic(Car)"                                "itraffic_car",             "DOUBLE PRECISION")
    ]
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
COORD_DEC_PRECISION = 6

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
    def __init__(self, path_template, vernum, queue, (srid, prjwkt), max_queue_depth, single_load_visum):
        super(VisumManager, self).__init__()
        self.path_template = path_template
        self.vernum = vernum
        self.queue = queue
        self._threads = []
        self.srid = srid
        self.prjwkt = prjwkt
        self.max_queue_depth = max_queue_depth
        self.single_load_visum = single_load_visum
        logger.debug("VisumManager.__init__(): Done")
    def run(self):
        semaphore = None
        if (self.single_load_visum):
            semaphore = threading.Semaphore()
        getnetobj = True
        for TOD in self.TODs:
            v = VisumDataMiner(
                self.path_template.format(**{"tod":TOD}),
                self.vernum,
                getnetobj,
                self.queue,
                (self.srid, self.prjwkt),
                semaphore
            )
            v.start()
            self._threads.append(v)
            if getnetobj:
                getnetobj = False
        for t in self._threads:
            t.join()

class VisumDataMiner(threading.Thread):
    def __init__(self, path, vernum, getnetobj, queue, (srid, prjwkt), semaphore):
        super(VisumDataMiner, self).__init__()
        self.path = path
        self.vernum = vernum
        self.getnetobj = getnetobj
        self.queue = queue
        self._index_templates = {}
        self.tod = None
        self.srid = srid
        self.prjwkt = prjwkt
        self.semaphore = semaphore
        logger.debug("VisumDataMiner.__init__(): Done")

    def run(self):
        sys.coinit_flags = 0 
        pythoncom.CoInitialize()
        if self.semaphore:
            self.semaphore.acquire()
        v = self.CreateVisum()
        self.semaphore.release()
        v.Net.SetProjection(self.prjwkt, calculate = True)
        self.tod = v.Net.AttValue("TOD")
        v.Net.SetAttValue("CoordDecPlaces", COORD_DEC_PRECISION)

        if self.getnetobj:
            self.GetNetObjects(v)
        self.GetAttributes(v)
        self.GetMatrices(v)
        if self.getnetobj:
            self.GetGeometries(v)

        pythoncom.CoUninitialize()
        logger.debug("VisumDataMiner-%s.run(): Finished", self.tod)

    def CreateVisum(self):
        v = win32com.client.Dispatch("Visum.Visum-64.{vn}".format(**{"vn":self.vernum}))
        v.LoadVersion(self.path)
        return v

    def _getAttributes(self, Visum, netobj, ids):
        return zip(*map(lambda (_id, dtype):self.GetVisumAttribute(Visum, netobj, _id), ids))
    def GetNetObjects(self, Visum):
        for netobj, ids in self.iterNetObjGroupIDs():
            logger.info("VisumDataMiner-%s.GetNetObjects(): Exporting NetObj %s", self.tod, netobj)
            data = self._getAttributes(Visum, netobj, ids)
            if len(data) > 0:
                self.queue.put(Sponge(**{
                    "type": database.TBL_NETOBJ,
                    "netobj": netobj,
                    "atts": ids,
                    "data": data
                }))
    def GetAttributes(self, Visum):
        for netobj, ids in self.iterNetObjGroupAttributes():
            logger.info("VisumDataMiner-%s.GetAttributes(): Exporting NetObj %s", self.tod, netobj)
            if not netobj in NETOBJ_IDs:
                logger.error("VisumDataMiner-%s.GetAttributes(): Error, {0} not included in NETOBJ_IDs".format(netobj), self.tod)
                continue
            ids = NETOBJ_IDs[netobj] + ids
            data = self._getAttributes(Visum, netobj, ids)
            if len(data) > 0:
                self.queue.put(Sponge(**{
                    "type": database.TBL_DATA,
                    "tod": self.tod,
                    "netobj": netobj,
                    "atts": ids,
                    "data": data
                }))
    def GetMatrices(self, Visum):
        for mtxno in self.iterMatrices():
            logger.info("VisumDataMiner-%s.GetMatrices(): Exporting Matrix %s", self.tod, mtxno)
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
        logger.info("VisumDataMiner-%s.GetGeometries(): Started", self.tod)
        # for netobj, geomfields in self.iterNetObjectGroup(self._getGeometryFields(Visum)):
        for netobj, ids in self.iterNetObjGroupIDs():
            geomfields = list(Utility.FindWKT(Visum, netobj))
            if not len(geomfields) > 0:
                logger.info("VisumDataMiner-%s.GetGeometries(): %s has no geometry", self.tod, netobj)
                continue
            if not getattr(Visum.Net, netobj).Count > 0:
                logger.info("VisumDataMiner-%s.GetGeometries(): %s has no objects", self.tod, netobj)
                continue
            if not netobj in NETOBJ_IDs:
                logger.warning("VisumDataMiner-%s.GetGeometries(): Warning, %s not included in NETOBJ_IDs", self.tod, netobj)
                continue
            logger.debug("VisumDataMiner-%s.GetGeometries(): Exporting geometries from Netobj %s", self.tod, netobj)
            gatts = []
            gdata = []
            # atts = NETOBJ_IDs[netobj]
            # data = self._getAttributes(Visum, netobj, atts)
            data = self._getAttributes(Visum, netobj, ids)
            for gfield in geomfields:
                _data = self.GetVisumAttribute(Visum, netobj, gfield)
                gdtype = self._extractFeatureType(_data)
                gatts.append((gfield, gdtype))
                gdata.append(map(
                    lambda v:"SRID={srid};".format(**{"srid":self.srid}) + v,
                    _data
                ))
            self.queue.put(Sponge(**{
                "type": database.TBL_GEOMETRY,
                "netobj": netobj,
                "atts": ids,
                "data": data,
                "gatts": gatts,
                # Internal debate about this, it'll get 'appended' to data which involves zip(*args) both
                # For now, transpose for consistency sake
                "gdata": zip(*gdata),
                "srid": self.srid
            }))
    def _getGeometryFields(self, Visum):
        netobj_geometry = {}
        attributes = Utility.GetCOMAttributes(Visum)
        wkt_fields = filter(lambda row:"wkt" in row[1].lower(), attributes)
        logger.info("VisumDataMiner-%s._getGeometryFields(): Found %s geometry fields", self.tod, len(wkt_fields))
        for netobj in set(zip(*wkt_fields)[0]):
            netobj_geometry[netobj] = zip(*filter(lambda row:row[0] == netobj, wkt_fields))[1]
        return netobj_geometry

    @staticmethod
    def _extractFeatureType(features):
        # gdtype = set(zip(*map(lambda v:v.split("(",1), features))[0])
        gdtype = set(zip(*map(lambda v:re.split(" |\(", v, 1), features))[0])
        assert len(gdtype) == 1, "Too many feature types (%s)" % str(gdtype)
        return list(gdtype)[0]
    @staticmethod
    def GetVisumAttribute(Visum, netobj, att):
        return map(lambda (i,v):v, getattr(Visum.Net, netobj).GetMultiAttValues(att, False))
    @staticmethod
    def GetVisumMatrix(Visum, mtxno):
        return numpy.array(Visum.Net.Matrices.ItemByKey(mtxno).GetValues())
    @staticmethod
    def iterNetObjIDs():
        for netobj, ids in NETOBJ_IDs.iteritems():
            for _id, dtype in ids:
                yield netobj, _id
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
    # Note:
    # When I run this on my local (work) machine, it works. (Visum 15.22-x64)
    #   Win 7 Pro; i7-3770; 32 GB; OEM Python 2.7 x64
    # When I run this on one of the workstations, it fails. (Visum 15.14 x64, Visum 15.22 x64)
    #   Win 7 Pro; e5-2687W v4; 256 (192) GB; Continuum Anaconda 2.7 x64
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
    @staticmethod
    def FindWKT(Visum, netobj):
        for att in getattr(Visum.Net, netobj).Attributes.GetAll:
            if "wkt" in att.Code.lower():
                yield att.Code.lower()
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
    try:
        pypyodbc = __import__("pypyodbc")
    except:
        pypyodbc = None
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
        assert pypyodbc is not None, "Module pypyodbc not found"
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