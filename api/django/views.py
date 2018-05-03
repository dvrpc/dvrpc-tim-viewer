from django.http import *
from . import credentials
import psycopg2 as psql
import json
import time

JSON_MIME_TYPE = "application/json"

ERR_INVALID_HTTP_METHOD = "Unsupported HTTP Method"
ERR_INVALID_RESOURCE = "Invalid resource?"

URLPARAM_POINT = "p"
URLPARAM_LINE = "l"
URLPARAM_POLYGON = "g"
URLPARAM_DATA = "d"
URLPARAM_GEOJSON = "g"
URLPARAM_TEMPORALDATA = "t"

GEOMTYPE_POINT = "wktloc"
GEOMTYPE_LINE = "wktpoly"
GEOMTYPE_POLYGON = "wktsurface"

def _deathRattle(message):
    return HttpResponse(
        json.dumps({"message": message}),
        content_type = JSON_MIME_TYPE
    )
def index(request, *args, **kwds):
    return _deathRattle(ERR_INVALID_RESOURCE)

def _getPSQLCon():
    return psql.connect(**credentials.PSQL_CREDENTIALS)

def _runQry(qry_string, qry_params = None):
    con = _getPSQLCon()
    cur = con.cursor()
    cur.execute(qry_string, qry_params)
    return cur.fetchall()

def jsonQry(qry_string, qry_params = None):
    response, = _runQry(qry_string, qry_params)[0]
    return HttpResponse(
        response,
        content_type = JSON_MIME_TYPE
    )
def tableQry(qry_string, qry_params = None):
    response = _runQry(qry_string, qry_params)
    return HttpResponse(
        json.dumps(response),
        content_type = JSON_MIME_TYPE
    )


def schema(request, *args, **kwds):
    qry = "SELECT tim_getschema();"
    return jsonQry(qry)

def _parseGETArray(prefix, GETParams):
    '''
    Parse encoded array in GET request
    Reads input like: attn=3&att0=0&att1=1&att2=2&att3=3
    Parses to [0,1,2]
    Returns tuple of (exists::boolean, values::list, unbounded::boolean)
    '''
    numElemsKey = "%sn" % prefix
    elems = []
    exists, numElems = checkAttr(numElemsKey, GETParams)
    if not exists or numElems is None:
        return False, None, None
    try:
        numElems = int(numElems)
    except:
        return False, None, None
    if numElems > 0:
        for i in xrange(numElems):
            elemKey = "%s%d" % (prefix, i)
            if elemKey in GETParams:
                elems.append(GETParams[elemKey])
        return True, elems, False
    else:
        return True, None, True

def checkArrayAttr(attr, GETParams):
    numElemsKey = "%sn" % attr
    if attr in GETParams:
        return [GETParams[attr]], False
    elif numElemsKey in GETParams:
        exists, vals, unbounded = _parseGETArray(attr, GETParams)
        if exists:
            return vals, unbounded
        else:
            return None, None
    else:
        return None, None

def checkAttr(attr, GETParams):
    '''
    Check if param exists in GET request
    Returns tuple of (exists::boolean, value::string)
    '''
    if attr in GETParams:
        if GETParams[attr] == "":
            return True, None
        else:
            return True, GETParams[attr]
    else:
        return False, None

def directory(request, resource, *args, **kwds):
    _start_time = time.time()
    if resource in DIRECTORY:
        if request.method == "GET":
            return operator(resource, request.GET, _start_time)
        elif request.method == "POST":
            return operator(resource, request.POST, _start_time)
        else:
            return _deathRattle(ERR_INVALID_HTTP_METHOD)
    return _deathRattle(ERR_INVALID_RESOURCE)

def operator(netobj, params, *args, **kwds):
    _start_time = args[0]
    return HttpResponse(json.dumps({
            "resource": netobj,
            "params": params,
            "tods": checkArrayAttr("tod", params),
            "debugflag": checkAttr("debugflag", params),
            # "_args": args,
            "prctime": (time.time() - _start_time) * 1000
        }),
        content_type = JSON_MIME_TYPE
    )

def _checkKeys(netobj, netobj_keys):
    _qry = "SELECT field FROM tim_netobj_keys WHERE netobj = %s::TEXT;"
    payload = _runQry(_qry, (netobj,))
    if len(payload) > 0:
        if len(set(zip(*payload)[0]).difference(netobj_keys)) > 0:
            return False
        else:
            return True
    else:
        return False


DIRECTORY = set([

    "schema",

    "alias",
    "block",
    "blockitem",
    "blockitemtype",
    "blockversion",
    "calendarperiod",
    "chainedupvehjourneysection",
    "connector",
    "coordgrp",
    "coordgrpitem",
    "countlocation",
    "crosswalktemplate",
    "demandsegment",
    "demandsegtimevaryingatt",
    "detector",
    "direction",
    "edge",
    "edgeitem",
    "faceitem",
    "faresupplementitem",
    "faresystem",
    "farezone",
    "fleetcomposition",
    "fleetcompositiontovehiclestratum",
    "fromtozonefareitem",
    "geometrytemplateitem",
    "holidays",
    "info",
    "intergreen",
    "lane",
    "laneturn",
    "leg",
    "legtemplateitem",
    "line",
    "lineroute",
    "linerouteitem",
    "link",
    "linkpoly",
    "linktimevaryingatt",
    "linktype",
    "mainnode",
    "mainnodetimevaryingatt",
    "mainturn",
    "mainturntimevaryingatt",
    "mainzone",
    "mode",
    "node",
    "nodetimevaryingatt",
    "operator",
    "path",
    "pathitem",
    "point",
    "poiofcat_1",
    "poiofcat_10",
    "poiofcat_11",
    "poiofcat_12",
    "poiofcat_13",
    "poiofcat_14",
    "poiofcat_15",
    "poiofcat_18",
    "poiofcat_3",
    "poiofcat_4",
    "poiofcat_5",
    "poiofcat_8",
    "poiofcat_9",
    "poitolink",
    "poitonode",
    "screenline",
    "screenlinepoly",
    "signalcontrol",
    "signalcoordgroup",
    "signalgroup",
    "signalgrouptemplate",
    "signalgrouptemplateitem",
    "stage",
    "stagetemplate",
    "stagetemplateitem",
    "stagetemplateset",
    "stagetemplatesetitem",
    "stop",
    "stoparea",
    "stoppoint",
    "surfaceitem",
    "sysroute",
    "sysrouteitem",
    "sysroutevehtime",
    "territory",
    "tickettype",
    "timeprofile",
    "timeprofileitem",
    "tollsystem",
    "transferfare",
    "transferwaittimetp",
    "transferwaittimetsys",
    "transferwalktimedirline",
    "transferwalktimestoparea",
    "transferwalktimetp",
    "transferwalktimetsys",
    "tsys",
    "turn",
    "turnstandard",
    "turntimevaryingatt",
    "userattdef",
    "validdays",
    "vehcomb",
    "vehjourney",
    "vehjourneycouplesectionitem",
    "vehjourneysection",
    "vehunit",
    "vehunittovehcomb",
    "zone",
    "zonecountfareitem",

])
