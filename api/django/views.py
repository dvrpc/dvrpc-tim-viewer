from django.http import *
from . import credentials
import psycopg2 as psql
import json

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
        content_type = 'text/javascript'
    )

def schema(request, *args, **kwds):
    qry = "SELECT tim_getschema();"
    return jsonQry(qry)

def argkwds(request, *args, **kwds):
    # URL: /argkwds/?a&b=1
    # response.GET: {"a": "", "b": "1"}
    return HttpResponse(json.dumps(request.GET))