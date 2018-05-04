from django.http import *
from . import credentials
import psycopg2 as psql
import json
import time

JSON_MIME_TYPE = "application/json"

ERR_INVALID_HTTP_METHOD = "Unsupported HTTP Method"
ERR_INVALID_RESOURCE = "Invalid resource"

URLPARAM_KEY_DATATYPE = "t"
URLPARAM_KEY_GEOMTYPE = "g"
URLPARAM_KEY_ATTR = "f"
URLPARAM_KEY_MATRIX = "m"
URLPARAM_KEY_OZONE = "oz"
URLPARAM_KEY_DZONE = "dz"
URLPARAM_KEY_TOD = "tod"
URLPARAM_KEY_SCEN = "s"

URLPARAM_VALUE_POINT = "p"
URLPARAM_VALUE_LINE = "l"
URLPARAM_VALUE_POLYGON = "g"
URLPARAM_VALUE_DATA = "d"
URLPARAM_VALUE_GEOJSON = "g"
URLPARAM_VALUE_TEMPORALDATA = "t"

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



def _getNetObjKeys(netobj):
    _qry = "SELECT field FROM tim_netobj_keys WHERE netobj = %s::TEXT;"
    return zip(*_runQry(_qry, (netobj,)))[0]

def _extractKeys(keys, assarr):
    xkvp = map(lambda k:(k, assarr[k]) if k in assarr else (None, None), keys)
    xkvp = dict(xkvp)
    if None in xkvp:
        return False, None
    else:
        return True, xkvp

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

# ---- #

def schema(request, *args, **kwds):
    qry = "SELECT tim_getschema();"
    return jsonQry(qry)
def _desireLines(param, dlType = None, *args, **kwds):
    '''
    type::text
    
    matrixNo::INTEGER - 'm'
    origzonenos::INTEGER[] - 'oz'
    destzonenos::INTEGER[] - 'dz'
    tods::TEXT[] - 'tod'
    
    TODO: scen::TEXT
    '''
    
    return HttpResponse(json.dumps({
        "param": param,
        "required": {
            URLPARAM_KEY_DATATYPE: dlType if dlType else checkAttr(URLPARAM_KEY_DATATYPE, param),
            URLPARAM_KEY_MATRIX: checkAttr(URLPARAM_KEY_MATRIX, param),
            URLPARAM_KEY_OZONE: checkArrayAttr(URLPARAM_KEY_OZONE, param),
            URLPARAM_KEY_DZONE: checkArrayAttr(URLPARAM_KEY_DZONE, param),
            URLPARAM_KEY_TOD: checkArrayAttr(URLPARAM_KEY_TOD, param),
            URLPARAM_KEY_SCEN: checkAttr(URLPARAM_KEY_SCEN, param),
        }
    }), content_type = JSON_MIME_TYPE)
def ddl(param, *args, **kwds):
    return _desireLines(param, "ddl", *args, **kwds)
def vddl(param, *args, **kwds):
    return _desireLines(param, "vddl", *args, **kwds)

# ---- #

def directory(request, resource, *args, **kwds):
    _start_time = time.time()
    param = {}
    if request.method == "GET":
        param = request.GET
    elif request.method == "POST":
        param = request.POST
    else:
        return _deathRattle(ERR_INVALID_HTTP_METHOD)
    if resource in PROCEDURES:
        return PROCEDURES[resource](param, *args, **kwds)
    elif resource in NETOBJS:
        return operator(resource, param, _start_time)
    else:
        return _deathRattle(ERR_INVALID_RESOURCE)

def operator(netobj, params, *args, **kwds):
    _start_time = args[0]
    req_keys = _getNetObjKeys(netobj)

    return HttpResponse(json.dumps({
            "resource": netobj,
            "params": params,
            "tods": checkArrayAttr("tod", params),
            "reqkeys": req_keys,
            "fields": checkArrayAttr(URLPARAM_KEY_ATTR, params),
            "foundkeys": _extractKeys(req_keys, params),
            "debugflag": checkAttr("debugflag", params),
            # "_args": args,
            "prctime": (time.time() - _start_time) * 1000
        }),
        content_type = JSON_MIME_TYPE
    )

# ---- #

PROCEDURES = {
    "schema": schema,
    "vddl": vddl,
    "ddl": ddl,
}

NETOBJS = set([
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
