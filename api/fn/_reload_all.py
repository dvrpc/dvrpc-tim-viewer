import os

import psycopg2 as psql

def main():
    con = psql.connect(
        user = "postgres",
        password = "sergt",
        host = "localhost",
        port = 5432,
        database = "dvrpc-tim-viewer"
    )
    cur = con.cursor()
    # FN FNS-9, little brother to the FN FNP-45, FNX-45
    fns = filter(lambda f:f.lower().endswith("sql"), os.listdir(os.curdir))
    for f in fns:
        with open(f, "rb") as io:
            cur.execute(io.read())
    con.commit()
    con.close()

if __name__ == "__main__":
    main()