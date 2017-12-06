import pythoncom
import sys
import threading
import win32com.client

import numpy

import database

import time

# Generated automanually using Utility.get_attributes below
# and manually finding identifying fields
NETOBJ_IDs = {
    "NotepadLines": ("index",), # OK
    "POICategories": ("no",), # OK
    "ValidDaysCont": ("no",), # OK
    "TSystems": ("code",), # OK
    "Modes": ("code",), # OK
    "DemandSegments": ("code",), # OK
    "Directions": ("no",), # OK
    "Nodes": ("no",), # OK
    "MainZones": ("no",), # OK
    "Zones": ("no",), # OK
    "LinkTypes": ("no",), # OK
    "Links": ("no","fromnodeno", "tonodeno"), # OK
    "Turns": ("fromnodeno", "tonodeno", "vianodeno"), # OK
    "Connectors": ("zoneno", "nodeno", "direction"), # OK
    "Operators": ("no",), # OK
    "Territories": ("no",), # OK
    "Stops": ("no",), # OK
    "StopAreas": ("no",), # OK
    "StopPoints": ("no",), # OK
    "MainLines": ("name",), # OK
    "Lines": ("name",), # OK
    "LineRoutes": ("linename", "name", "directioncode"), # OK
    "LineRouteItems": ("linename", "lineroutename", "directioncode", "index"), # OK
    "TimeProfiles": ("linename", "lineroutename", "directioncode", "name"), # OK
    "TimeProfileItems": ("linename", "lineroutename", "directioncode", "index"), # OK
    "VehicleJourneys": ("name",), # OK
    "VehJourneySections": ("vehjourneyno", "no"), # OK
    "CountLocations": ("no",), # OK
    "Screenlines": ("no",), # OK
}

_invalid_NETOBJ_IDs = {
    "[User-Defined Attributes]": (), # No Identifiers
    "[Network]": (), # No Identifiers
    "[Fare Model]": (), # No Identifiers
    "[Fare Systems]": ("no",),
    "[Transfer Fares]": ("fromfsysno", "tofsysno"),
    "[Points]": ("id",),
    "[Edges]": ("id",),
    "[Intermediate Points]": ("edgeid", "index"),
    "[Faces]": ("id",),
    "[Face Items]": ("faceid", "index"),
    "[Surfaces]": ("id",),
    "[Surface Items]": ("surfaceid", "faceid"),
    "[Link Polygons]": ("fromnodeno", "tonodeno", "index"),
    "[Chained up vehicle journey sections]": ("vehjourneyno", "vehjourneysectionno", "calendarday"),
    "[Transfer Walk times between stop areas]": ("fromstopareano", "tostopareano", "tsyscode"),
    "[Fare Zones]": ("tickettypeno", "tsyscode"),
    "[Stop to fare zones]": ("farezoneno", "stopno"),
    "[Ticket types]": ("no",),
    "[Fare Supplements]": ("tickettypeno", "tsyscode"),
    "[Zone count fare items]": ("tickettypeno", "numfarezones"),
    "[From-to-Zone fare items]": ("tickettypeno", "fromfarezoneno", "tofarezoneno"),
    "[Fare system ticket types by Dseg]": ("tickettypeno", "dsegcode", "fsysno"),
    "[Block Versions]": ("id",),
    "[Points of Interest]": ("catno", "no"),
    "[POI to links]": ("poicatno", "poino", "fromnodeno", "tonodeno"),
    "[Screenline polygons]": ("screenlineno", "index"),
    "[Lanes]": ("nodeno", "mainnodeno", "linkno", "no", "approachtype"),
    "[Lane turns]": ("nodeno", "mainnodeno", "fromlinkno", "fromlaneno", "tolinkno", "tolaneno"),
    "Legs": ("nodeno", "mainnodeno", "orientation"), # Missing from COM
    "CalendarPeriod": ("no",), # Missing from COM
}

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

# I knew I wanted a thread manager
class VisumManager(threading.Thread):
    TODs = ["AM","MD","PM","NT"]
    def __init__(self, path_template, vernum, queue):
        super(VisumManager, self).__init__()
        self.path_template = path_template
        self.vernum = vernum
        self.queue = queue
    def run(self):
        for TOD in self.TODs:
            print "TOD",
            v = Visum(self.path_template.format(**{"tod":TOD}), self.vernum, self.queue)
            print "start",
            v.start()
            v.join()
            print "done"

class Visum(threading.Thread):
    def __init__(self, path, vernum, queue):
        super(Visum, self).__init__()
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
        # self.GetAttributes(v)
        # self.GetMatrices(v)
        # self.GetGeometries(v)
        pythoncom.CoUninitialize()

    def CreateVisum(self):
        v = win32com.client.Dispatch("Visum.Visum-64.{vn}".format(**{"vn":self.vernum}))
        v.LoadVersion(self.path)
        return v

    def GetNetObjects(self, Visum):
        for netobj, ids in self.iterNetObjGroupIDs():
            payload = zip(*map(lambda id:self.GetVisumAttribute(Visum, netobj, id), ids))
            if len(payload) > 0:
                self.queue.put(Sponge(**{
                    "type": database.TBL_NETOBJ,
                    "tod": self.tod,
                    "netobj": netobj,
                    "atts": ids,
                    "data": payload
                }))
    def GetAttributes(self, Visum):
        for netobj, ids in self.iterNetObjIDs():
            self.queue.put(Sponge(**{
                "type": database.TBL_DATA,
                "tod": self.tod,
                "netobj": netobj,
                "atts": ids,
                "data": getattr(Visum.Net, netobj).GetMultiAttValues(id)
            }))
    def GetMatrices(self, Visum):
        for mtxno in self.iterMatrices():
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
    def GetGeometries(self):
        pass

    @staticmethod
    def GetVisumAttribute(Visum, netobj, att):
        return map(lambda (i,v):v, getattr(Visum.Net, netobj).GetMultiAttValues(att))
    @staticmethod
    def GetVisumMatrix(Visum, mtxno):
        return numpy.array(Visum.Net.Matrices.ItemByKey(mtxno).GetValues())
    @staticmethod
    def iterNetObjIDs():
        for netobj, ids in NETOBJ_IDs.iteritems():
            for id in ids:
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
        pass

class Sponge:
    def __init__(self, **kwds):
        for k, v in kwds.iteritems():
            setattr(self, k, v)
    def __contains__(self, key):
        return hasattr(self, key)

class Utility:
    def __init__(self):
        pass
    @staticmethod
    def enumerateCOM(object, bruteforcen = 1000):
        methods, attributes = [], []
        for i in xrange(bruteforcen):
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
    @classmethod
    def get_attributes(self, VisumCOM):
        master_attributes = []
        methods, attributes = self.enumerateCOM(VisumCOM.Net)
        for (att,) in sorted(attributes):
            COMobj = getattr(VisumCOM.Net, att)
            _methods, _attributes = enumerateCOM(COMobj)
            if ("Attributes",) in _attributes:
                for COMatt in COMobj.Attributes.GetAll:
                    master_attributes.append((att, COMatt.Code, COMatt.ValueType, COMatt.Source))