from django.http import *
from phltripgen import credentials
import psycopg2 as psql
import json
import time

JSON_MIME_TYPE = "application/json"

ERR_INVALID_HTTP_METHOD = "Unsupported HTTP Method"
ERR_INVALID_RESOURCE = "Invalid resource"
ERR_INCOMPLETE_PARAM = "Incomplete parameters"
ERR_INVALID_PARAM = "Invalid parameter"

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
        json.dumps(response),
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
    return list(zip(*_runQry(_qry, (netobj,))))[0]

def _extractKeys(keys, assarr):
    xkvp = map(lambda k:(k, assarr[k]) if k in assarr else (None, None), keys)
    xkvp = dict(xkvp)
    if None in xkvp:
        return False, None
    else:
        return True, xkvp

def _parseGETArray(prefix, params, dtype):
    '''
    Parse encoded array in GET request
    Reads input like: attn=3&att0=0&att1=1&att2=2&att3=3
    Parses to [0,1,2]
    Returns tuple of (exists::boolean, values::list, unbounded::boolean)
    '''
    numElemsKey = "%sn" % prefix
    elems = []
    exists, numElems = checkAttr(numElemsKey, params, dtype)
    if not exists or numElems is None:
        return False, (None, None)
    try:
        numElems = int(numElems)
    except:
        return False, (None, None)
    if numElems > 0:
        for i in range(numElems):
            elemKey = "%s%d" % (prefix, i)
            if elemKey in params:
                elems.append(params[elemKey])
        return _castableArrayAttr(elems, dtype)
    else:
        return True, (None, True)
def _castableAttr(attr, dtype):
    if dtype is str:
        return True, attr
    try:
        return True, dtype(attr)
    except:
        return False, None
def _castableArrayAttr(attr, dtype):
    if dtype is str:
        return True, (attr, False)
    try:
        return True, (map(dtype, attr), False)
    except:
        return False, (None, None)

def checkArrayAttr(attr, params, dtype):
    '''
    Returns tuple of (exists::boolean, values::list, unbounded::boolean)
    '''
    numElemsKey = "%sn" % attr
    if attr in params:
        return _castableArrayAttr([params[attr]], dtype)
    elif numElemsKey in params:
        return _parseGETArray(attr, params, dtype)
    else:
        return False, (None, None)
def checkAttr(attr, params, dtype):
    '''
    Check if param exists in GET request
    Returns tuple of (exists::boolean, value::string)
    '''
    if attr in params:
        if params[attr] == "":
            return True, None
        else:
            return _castableAttr(params[attr], dtype)
    else:
        return False, None
def checkArrayAttrKwd(attr, params, dtype, kwd = None):
    '''
    Check if kwd is not None, if it is return else checkArrayAttr
    '''
    return (True, (kwd, False)) if kwd is not None else checkArrayAttr(attr, params, dtype)
def checkAttrKwd(attr, params, dtype, kwd = None):
    '''
    Check if kwd is not None, if it is return else checkAttr
    '''
    return (True, kwd) if kwd is not None else checkAttr(attr, params, dtype)
def checkParams(param_dir, params):
    '''
    param_dir = {
        key: (checkFn, castDtype, defval), ...
    }
    Returns tuple of (complete::boolean, { key: (exists::boolean, fn(key, params, dtype, *defval)), ... })
    '''
    complete = True
    retval = {}
    for k, (fn, dtype, args) in param_dir.items():
        exists, _retval = fn(k, params, dtype, *args)
        if not exists:
            complete = False
        retval[k] = _retval
    return complete, retval

# ---- #

def schema(request, *args, **kwds):
    qry = "SELECT tim_getschema();"
    return jsonQry(qry)
def _desireLines(params, dlType = None, *args, **kwds):
    '''
    type::text
    
    matrixNo::INTEGER - 'm'
    origzonenos::INTEGER[] - 'oz'
    destzonenos::INTEGER[] - 'dz'
    tods::TEXT[] - 'tod'
    
    TODO: scen::TEXT
    '''
    req_param = {
    #   param                   checkFn         type    defval
        URLPARAM_KEY_DATATYPE: (checkAttrKwd,   str,   (dlType,)),
        URLPARAM_KEY_MATRIX:   (checkAttr,      int,   ()),
        URLPARAM_KEY_TOD:      (checkArrayAttr, str,   ()),
        URLPARAM_KEY_OZONE:    (checkArrayAttr, int,   ()),
        URLPARAM_KEY_DZONE:    (checkArrayAttr, int,   ()),
    }

    ok, parsed_param = checkParams(req_param, params)

    if not ok:
        return _deathRattle(ERR_INCOMPLETE_PARAM)

    _dlType = parsed_param[URLPARAM_KEY_DATATYPE]
    if _dlType != "ddl" and _dlType != "vddl":
        return _deathRattle(ERR_INVALID_PARAM)

    qry = "SELECT tim_gfx_%s(%%s, %%s, %%s, %%s)" % _dlType

    mtxno =         parsed_param[URLPARAM_KEY_MATRIX]
    ozonenos, all = parsed_param[URLPARAM_KEY_OZONE]
    dzonenos, all = parsed_param[URLPARAM_KEY_DZONE]
    tods, all =     parsed_param[URLPARAM_KEY_TOD]

    return jsonQry(qry, [
        mtxno,
        ozonenos,
        dzonenos,
        tods
    ])

def desireline(param, *args, **kwds):
    return _desireLines(param)
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

    if   't' not in params:
        return _deathRattle(ERR_INCOMPLETE_PARAM)
    elif params['t'] == 'g':
        return getGeoJSON(netobj, params)
    elif params['t'] == 'a':
        getRecords(netobj, params)
    elif params['t'] == 't':
        getTemporalRecords(netobj, params)
    else:
        return _deathRattle(ERR_INCOMPLETE_PARAM)

    return HttpResponse(json.dumps({
            "resource": netobj,
            "params": params,
            "tods": checkArrayAttr(URLPARAM_KEY_TOD, params, str),
            "reqkeys": req_keys,
            "fields": checkArrayAttr(URLPARAM_KEY_ATTR, params, str),
            "foundkeys": _extractKeys(req_keys, params),
            "prctime": (time.time() - _start_time) * 1000,
        }),
        content_type = JSON_MIME_TYPE
    )

def getRecords(netobj, params):
    pass
def getSingleRecord():
    pass
def getMultipleRecords():
    pass
def getFilteredRecords():
    pass

def getGeoJSON(netobj, params):
    if   'g' not in params:
        return _deathRattle(ERR_INCOMPLETE_PARAM)
    elif params['g'] == 'p':
        geomtype = "wktloc"
    elif params['g'] == 'l':
        geomtype = "wktpoly"
    elif params['g'] == 'g':
        geomtype = "wktsurface"
    else:
        return _deathRattle(ERR_INCOMPLETE_PARAM)
    try:
        return jsonQry("SELECT tim_gfx_netobj(%s,%s)", [
            netobj, geomtype
        ])
    except psql.errors.UndefinedColumn:
        return _deathRattle(ERR_INVALID_PARAM)


def getTemporalRecords(netobj, params):
    pass
def getSingleTemporalRecord():
    pass
def getMultipleTemporalRecords():
    pass
def getFilteredTemporalRecords():
    pass

# ---- #

PROCEDURES = {
    "schema": schema,
    "desireline": desireline,
    "vddl": vddl,
    "ddl": ddl,
}

NETOBJS = set([
    "connectors",
    "countlocations",
    "linerouteitems",
    "lineroutes",
    "lines",
    "links",
    "linktypes",
    "nodes",
    "screenlines",
    "stopareas",
    "stoppoints",
    "stops",
    "territories",
    "timeprofileitems",
    "timeprofiles",
    "vehiclecombinations",
    "vehiclejourneyitems",
    "vehiclejourneys",
    "zones",
])
