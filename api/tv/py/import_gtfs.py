import csv
import zipfile
import os
import hashlib

import psycopg2 as psql

GTFS_ZIP = r"Z:\downloads\google_rail.zip"

GTFS_SCHEMA = {
    "agency": [
        ("agency_id",               "TEXT NOT NULL"),
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

GTFS_ID = None

def filter_gtfs_table(header, data):
    return zip(*filter(lambda col:col[0].strip() in header, zip(*data)))
def prepend_gtfs_id(data):
    for row in data:
        yield [GTFS_ID] + list(row)

con = psql.connect(
    host = "wol-vm-pubsql",
    port = 5432,
    database = "trainview",
    user = "",
    password = ""
)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS gtfs_meta (gtfs_id SMALLINT, hash TEXT)")

hash = hashlib.md5()
with open(GTFS_ZIP, "rb") as io:
    hash.update(io.read())
hash = hash.hexdigest()

cur.execute("SELECT gtfs_id FROM gtfs_meta WHERE hash = %s", (hash,))
if cur.fetchone() is None:
    cur.execute("SELECT max(gtfs_id) FROM gtfs_meta")
    (_max_gtfs_id,) = cur.fetchone()
    GTFS_ID = _max_gtfs_id + 1
    cur.execute("INSERT INTO gtfs_meta VALUES (%s, %s)", (GTFS_ID, hash))
    gtfs_data = {}

    with zipfile.ZipFile(GTFS_ZIP) as zf:
        for f in zf.namelist():
            gtfs_table, _ = os.path.splitext(f)
            if gtfs_table in GTFS_SCHEMA:
                with zf.open(f) as io:
                    r = csv.reader(io)
                    gtfs_data[gtfs_table] = filter_gtfs_table(zip(*GTFS_SCHEMA[gtfs_table])[0], [row for row in r])

    for gtfs_table, field_defs in GTFS_SCHEMA.iteritems():
        cur.execute(SQL_CREATE % (gtfs_table, ",".join("%s %s" % (f, d) for f, d in field_defs)))
    for gtfs_table, table in gtfs_data.iteritems():
        print gtfs_table
        header = table[0]
        cur.executemany(SQL_INSERT % (gtfs_table, ",".join(header), ",".join("%s" for _ in header)), prepend_gtfs_id(table[1:]))
    con.commit()

else:
    print "Already imported"