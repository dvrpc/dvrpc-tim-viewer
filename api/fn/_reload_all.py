import os

import psycopg2 as psql

from credentials import *

def main():
    con = psql.connect(**PSQL_CNX)
    cur = con.cursor()
    fns = filter(lambda f:f.lower().endswith("sql"), os.listdir(os.curdir))
    for f in fns:
        with open(f, "rb") as io:
            cur.execute(io.read())
    con.commit()
    con.close()

if __name__ == "__main__":
    main()