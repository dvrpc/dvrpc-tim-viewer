import csv
import hashlib
import io
import os
import zipfile

import psycopg2 as psql

GTFS_SCHEMA = {
    "agency": [
        ("agency_id",               "TEXT"), # Fuck you SEPTA. GTFS spec dictates NOT NULL
        ("agency_name",             "TEXT NOT NULL"),
        ("agency_url",              "TEXT NOT NULL"),
        ("agency_timezone",         "TEXT NOT NULL"),
        ("agency_lang",             "TEXT"),
        ("agency_phone",            "TEXT"),
        ("agency_fare_url",         "TEXT"),
        ("agency_email",            "TEXT"),
    ],
    "stops": [
        ("stop_id",                 "TEXT NOT NULL"),
        ("stop_code",               "TEXT"),
        ("stop_name",               "TEXT NOT NULL"),
        ("stop_desc",               "TEXT"),
        ("stop_lat",                "REAL NOT NULL"),
        ("stop_lon",                "REAL NOT NULL"),
        ("zone_id",                 "TEXT"),
        ("stop_url",                "TEXT"),
        ("location_type",           "SMALLINT"),
        ("parent_station",          "TEXT"),
        ("stop_timezone",           "TEXT"),
        ("wheelchair_boarding",     "SMALLINT"),
    ],
    "routes": [
        ("route_id",                "TEXT NOT NULL"),
        ("agency_id",               "TEXT"),
        ("route_short_name",        "TEXT NOT NULL"),
        ("route_long_name",         "TEXT NOT NULL"),
        ("route_desc",              "TEXT"),
        ("route_type",              "SMALLINT NOT NULL"),
        ("route_url",               "TEXT"),
        ("route_color",             "TEXT"),
        ("route_text_color",        "TEXT"),
        ("route_sort_order",        "TEXT"),
    ],
    "trips": [
        ("route_id",                "TEXT NOT NULL"),
        ("service_id",              "TEXT NOT NULL"),
        ("trip_id",                 "TEXT NOT NULL"),
        ("trip_headsign",           "TEXT"),
        ("trip_short_name",         "TEXT"),
        ("direction_id",            "SMALLINT"),
        ("block_id",                "TEXT"),
        ("shape_id",                "TEXT"),
        ("wheelchair_accessible",   "SMALLINT"),
        ("bikes_allowed",           "SMALLINT"),
    ],
    "stop_times": [
        ("trip_id",                 "TEXT NOT NULL"),
        ("arrival_time",            "INTERVAL NOT NULL"),
        ("departure_time",          "INTERVAL NOT NULL"),
        ("stop_id",                 "TEXT NOT NULL"),
        ("stop_sequence",           "SMALLINT NOT NULL"),
        ("stop_headsign",           "TEXT"),
        ("pickup_type",             "SMALLINT"),
        ("drop_off_type",           "SMALLINT"),
        ("shape_dist_traveled",     "REAL"),
        ("timepoint",               "SMALLINT"),
    ],
    "calendar": [
        ("service_id",              "TEXT NOT NULL"),
        ("monday",                  "SMALLINT NOT NULL"),
        ("tuesday",                 "SMALLINT NOT NULL"),
        ("wednesday",               "SMALLINT NOT NULL"),
        ("thursday",                "SMALLINT NOT NULL"),
        ("friday",                  "SMALLINT NOT NULL"),
        ("saturday",                "SMALLINT NOT NULL"),
        ("sunday",                  "SMALLINT NOT NULL"),
        ("start_date",              "TIMESTAMP"),
        ("end_date",                "TIMESTAMP"),
    ],
    "calendar_dates": [
        ("service_id",              "TEXT NOT NULL"),
        ("date",                    "TIMESTAMP NOT NULL"),
        ("exception_type",          "SMALLINT NOT NULL"),
    ],
    "shapes": [
        ("shape_id",                "TEXT NOT NULL"),
        ("shape_pt_lat",            "DOUBLE PRECISION NOT NULL"),
        ("shape_pt_lon",            "DOUBLE PRECISION NOT NULL"),
        ("shape_pt_sequence",       "SMALLINT NOT NULL"),
        ("shape_dist_traveled",     "REAL"),
    ],
}

SQL_CREATE = "CREATE TABLE IF NOT EXISTS gtfs_%s (gtfs_id SMALLINT NOT NULL, %s)"
SQL_INSERT = "INSERT INTO gtfs_%s (gtfs_id,%s) VALUES (%%s,%s)"

def filter_gtfs_table(header, data):
    return zip(*filter(lambda col:col[0].strip() in header, zip(*data)))

def prepend_gtfs_id(gtfs_id, data):
    for row in data:
        yield [gtfs_id] + list(row)

def _parseZip(path):
    gtfs_data = {}
    with zipfile.ZipFile(path) as zf:
        for fn in zf.namelist():
            gtfs_table, _ = os.path.splitext(fn)
            if gtfs_table in GTFS_SCHEMA:
                with zf.open(fn) as f:
                    r = csv.reader(f)
                    gtfs_data[gtfs_table] = filter_gtfs_table(zip(*GTFS_SCHEMA[gtfs_table])[0], [row for row in r])
    return gtfs_data

def parseZip(path):
    hash = hashlib.md5()
    with open(path, "rb") as f:
        hash.update(f.read())
    return hash.hexdigest(), _parseZip(path)

def parseNestedZip(path):
    with zipfile.ZipFile(path) as zf:
        for subzip in zf.namelist():
            print subzip,
            szf = io.BytesIO(zf.read(subzip))
            hash = hashlib.sha256()
            hash.update(szf.read())
            szf.seek(0)
            gtfs_data = _parseZip(szf)
            yield hash.hexdigest(), _parseZip(szf)

def parseSEPTAZip(con, path):
    for hash, gtfs_data in parseNestedZip(path):
        gtfs_id = checkGTFSHash(con, hash)
        if gtfs_id is None:
            print "Exists"
            continue
        print gtfs_id
        insertGTFS(con, gtfs_id, gtfs_data)

def checkGTFSHash(con, hash):
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS gtfs_meta (gtfs_id SMALLINT, hash TEXT)")
    cur.execute("SELECT gtfs_id FROM gtfs_meta WHERE hash = %s", (hash,))
    if cur.fetchone() is None:
        cur.execute("SELECT max(gtfs_id) FROM gtfs_meta")
        (max_gtfs_id,) = cur.fetchone()
        if max_gtfs_id is None:
            max_gtfs_id = 0
        gtfs_id = max_gtfs_id + 1
        cur.execute("INSERT INTO gtfs_meta VALUES (%s, %s);", (gtfs_id, hash))
        con.commit()
        return gtfs_id
    else:
        return None

def insertGTFS(con, gtfs_id, gtfs_data):
    cur = con.cursor()
    for gtfs_table, field_defs in GTFS_SCHEMA.iteritems():
        cur.execute(SQL_CREATE % (gtfs_table, ",".join("%s %s" % (f, d) for f, d in field_defs)))
    for gtfs_table, table in gtfs_data.iteritems():
        header = table[0]
        cur.executemany(
            SQL_INSERT % (gtfs_table, ",".join(header), ",".join("%s" for _ in header)),
            prepend_gtfs_id(gtfs_id, table[1:])
        )
    con.commit()

if __name__ == "__main__":

    con = psql.connect(
        host = "localhost",
        port = 5432,
        database = "septatest",
        user = "postgres",
        password = "sergt"
    )

    parseSEPTAZip(con, r"C:\Users\wtsay\Downloads\gtfs_feeds\gtfs_public (3).zip")