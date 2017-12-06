import pythoncom
import sys
import threading
import win32com.client

Visum_IDs = {
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

_invalid_Visum_IDs = {
    "[User-Defined Attributes]": (),
    "[Network]": (),
    "[Fare Systems]": ("no",),
    "[Transfer Fares]": ("fromfsysno", "tofsysno"),
    "[Fare Model]": (),
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
    "Legs": ("nodeno", "mainnodeno", "orientation"), # Missing?
    "CalendarPeriod": ("no",), # Missing
}

class VisumManager(threading.Thread):
    def __init__(self, vernum):
        super(VisumManager, self).__init__()

    def run(self):
        pass

class Visum(threading.Thread):
    def __init__(self):
        super(VisumManager, self).__init__()

    def run(self):
        sys.coinit_flags = 0
        pythoncom.CoInitialize()

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
    def get_attributes(self):
        master_attributes = []
        methods, attributes = self.enumerateCOM(Visum.Net)
        for (att,) in sorted(attributes):
            COMobj = getattr(Visum.Net, att)
            _methods, _attributes = enumerateCOM(COMobj)
            if ("Attributes",) in _attributes:
                for COMatt in COMobj.Attributes.GetAll:
                    master_attributes.append((att, COMatt.Code, COMatt.ValueType, COMatt.Source))
